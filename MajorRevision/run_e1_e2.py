"""Run the major-revision semantic utility (E1) and privacy (E2) experiments.

The script deliberately rebuilds every learned transform after the temporal split.
It does not read the pre-trained models or the pre-computed fusion labels in v4-v6.
"""

from __future__ import annotations

import hashlib
import json
import math
import platform
import sys
import time
from dataclasses import dataclass
from pathlib import Path

import joblib
import matplotlib
import numpy as np
import pandas as pd
import scipy
import sklearn
from matplotlib import pyplot as plt
from scipy.special import erfcinv
from sklearn.decomposition import PCA
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    balanced_accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    roc_auc_score,
)
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.random_projection import GaussianRandomProjection


matplotlib.use("Agg")

ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "semantic_case_v6" / "data"
OUT_ROOT = ROOT / "MajorRevision"
E1_DIR = OUT_ROOT / "E1_semantic_utility"
E2_DIR = OUT_ROOT / "E2_privacy"
SEEDS = [3, 7, 11, 19, 23, 31, 42, 53, 71, 97]
PURGE_GAP = 10


WIRELESS_FEATURES = [
    "traffic_5g",
    "traffic_wifi",
    "traffic_lifi",
    "total_wireless_traffic",
    "wifi_signal_mean",
    "lifi_signal",
    "wifi_inactivity_mean",
    "traffic_fluctuation",
    "active_5g",
    "active_wifi",
    "active_lifi",
    "signal_quality",
]

PRIVATE_FEATURES = [
    "traffic_5g",
    "traffic_wifi",
    "traffic_lifi",
    "total_wireless_traffic",
    "wifi_signal_mean",
    "lifi_signal",
    "wifi_inactivity_mean",
    "traffic_fluctuation",
]

TARGET_COLUMNS = [
    "wireless_load_score",
    "link_stability_score",
    "access_diversity_score",
    "congestion_risk",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def existing(frame: pd.DataFrame, columns: list[str]) -> list[str]:
    return [column for column in columns if column in frame.columns]


def safe_sum(frame: pd.DataFrame, columns: list[str]) -> pd.Series:
    columns = existing(frame, columns)
    return frame[columns].sum(axis=1) if columns else pd.Series(0.0, index=frame.index)


@dataclass
class MinMax:
    low: float
    high: float

    @classmethod
    def fit(cls, values: np.ndarray) -> "MinMax":
        values = np.asarray(values, dtype=float)
        return cls(float(np.nanmin(values)), float(np.nanmax(values)))

    def transform(self, values: np.ndarray) -> np.ndarray:
        denom = self.high - self.low
        if abs(denom) < 1e-12:
            return np.zeros_like(np.asarray(values, dtype=float))
        return (np.asarray(values, dtype=float) - self.low) / denom


def build_wireless_base() -> pd.DataFrame:
    path = SOURCE_DIR / "wireless_real_30s.csv"
    frame = pd.read_csv(path).fillna(0)
    frame["Time"] = pd.to_datetime(frame["Time"])
    frame = frame.sort_values("Time").reset_index(drop=True)

    traffic_5g = [
        "Total 5G Cell Uplink Traffic", "Total 5G Cell Downlink Traffic",
        "recv_CPE1_5G", "trans_CPE1_5G", "recv_CPE2_5G", "trans_CPE2_5G",
        "recv_CPE3_5G", "trans_CPE3_5G", "recv_CPE4_5G", "trans_CPE4_5G",
    ]
    traffic_wifi = [
        "rxBytes_CPE1_WiFi", "txBytes_CPE1_WiFi", "rxBytes_CPE2_WiFi", "txBytes_CPE2_WiFi",
        "rxBytes_CPE3_WiFi", "txBytes_CPE3_WiFi", "rxBytes_CPE4_WiFi", "txBytes_CPE4_WiFi",
        "recv_CPE1_wifi", "trans_CPE1_wifi", "recv_CPE2_wifi", "trans_CPE2_wifi",
        "recv_CPE3_wifi", "trans_CPE3_wifi", "recv_CPE4_wifi", "trans_CPE4_wifi",
    ]
    traffic_lifi = ["txBytes_CPE4_LiFi", "rxBytes_CPE4_LiFi", "trans_CPE4_lifi", "recv_CPE4_lifi"]
    wifi_signal = [f"signalAvg_CPE{i}_WiFi" for i in range(1, 5)]
    wifi_inactive = [f"inactiveTime_CPE{i}_WiFi" for i in range(1, 5)]

    base = pd.DataFrame({"time": frame["Time"]})
    base["traffic_5g"] = safe_sum(frame, traffic_5g)
    base["traffic_wifi"] = safe_sum(frame, traffic_wifi)
    base["traffic_lifi"] = safe_sum(frame, traffic_lifi)
    base["total_wireless_traffic"] = base[["traffic_5g", "traffic_wifi", "traffic_lifi"]].sum(axis=1)
    base["wifi_signal_mean"] = frame[existing(frame, wifi_signal)].mean(axis=1)
    base["lifi_signal"] = frame[existing(frame, ["signal_CPE4_LiFi"])].mean(axis=1)
    base["wifi_inactivity_mean"] = frame[existing(frame, wifi_inactive)].mean(axis=1)
    base["traffic_fluctuation"] = (
        base["total_wireless_traffic"].rolling(window=5, min_periods=1).std().fillna(0)
    )
    base["traffic_rolling_mean"] = base["total_wireless_traffic"].rolling(window=5, min_periods=1).mean()

    cpe_columns = {
        "CPE1": ["recv_CPE1_5G", "trans_CPE1_5G", "recv_CPE1_wifi", "trans_CPE1_wifi"],
        "CPE2": ["recv_CPE2_5G", "trans_CPE2_5G", "recv_CPE2_wifi", "trans_CPE2_wifi"],
        "CPE3": ["recv_CPE3_5G", "trans_CPE3_5G", "recv_CPE3_wifi", "trans_CPE3_wifi"],
        "CPE4": [
            "recv_CPE4_5G", "trans_CPE4_5G", "recv_CPE4_wifi", "trans_CPE4_wifi",
            "recv_CPE4_lifi", "trans_CPE4_lifi",
        ],
    }
    rat_columns = {"5G": traffic_5g, "WiFi": traffic_wifi, "LiFi": traffic_lifi}
    for name, columns in cpe_columns.items():
        base[f"private_{name}"] = safe_sum(frame, columns)
    for name, columns in rat_columns.items():
        base[f"private_{name}"] = safe_sum(frame, columns)
    base["dominant_cpe"] = base[[f"private_CPE{i}" for i in range(1, 5)]].idxmax(axis=1).str.replace(
        "private_", "", regex=False
    )
    base["dominant_rat"] = base[["private_5G", "private_WiFi", "private_LiFi"]].idxmax(axis=1).str.replace(
        "private_", "", regex=False
    )
    return base


def build_optical_aligned(wireless_times: pd.Series) -> pd.DataFrame:
    source = pd.read_csv(SOURCE_DIR / "voyager.csv", dtype=str)
    source = source[source["Timestamp"] != "Timestamp"].copy()
    source["Timestamp"] = pd.to_datetime(source["Timestamp"], errors="coerce")
    source = source.dropna(subset=["Timestamp"]).sort_values("Timestamp").reset_index(drop=True)
    ber_columns = [column for column in source.columns if column.startswith("Voyager_ch") and column.endswith("_BER")]
    for column in ber_columns:
        source[column] = pd.to_numeric(source[column], errors="coerce")
    source = source.dropna(subset=ber_columns, how="all").reset_index(drop=True)
    clean = source[ber_columns].fillna(1e-12).clip(lower=1e-12, upper=0.499999)
    q_values = np.sqrt(2.0) * erfcinv(2.0 * clean.to_numpy(dtype=float))

    optical = pd.DataFrame({"original_optical_timestamp": source["Timestamp"]})
    optical["ber_mean"] = clean.mean(axis=1)
    optical["ber_max"] = clean.max(axis=1)
    optical["ber_min"] = clean.min(axis=1)
    optical["ber_std"] = clean.std(axis=1)
    optical["q_factor_mean"] = q_values.mean(axis=1)
    optical["q_factor_min"] = q_values.min(axis=1)
    optical["q_factor_max"] = q_values.max(axis=1)
    optical["ber"] = optical["ber_max"]
    optical["q_factor"] = optical["q_factor_min"]
    for column in ber_columns:
        optical[column] = clean[column].to_numpy(dtype=float)

    # The campaigns do not overlap. This sequence mapping is retained only to
    # construct the explicitly labelled interoperability benchmark.
    positions = np.round(np.linspace(0, len(optical) - 1, num=len(wireless_times))).astype(int)
    aligned = optical.iloc[positions].reset_index(drop=True)
    aligned.insert(0, "time", pd.to_datetime(wireless_times).reset_index(drop=True))
    return aligned


def temporal_indices(sample_count: int) -> dict[str, np.ndarray]:
    cut1 = int(math.floor(0.60 * sample_count))
    cut2 = int(math.floor(0.80 * sample_count))
    return {
        "train": np.arange(0, cut1 - PURGE_GAP, dtype=int),
        "validation": np.arange(cut1, cut2 - PURGE_GAP, dtype=int),
        "test": np.arange(cut2, sample_count, dtype=int),
        "purged": np.concatenate([
            np.arange(cut1 - PURGE_GAP, cut1, dtype=int),
            np.arange(cut2 - PURGE_GAP, cut2, dtype=int),
        ]),
    }


def derive_semantics(base: pd.DataFrame, train_indices: np.ndarray) -> tuple[pd.DataFrame, dict]:
    frame = base.copy()
    train = frame.iloc[train_indices]
    active_thresholds = {
        rat: float(train[f"traffic_{rat}"].quantile(0.25)) for rat in ("5g", "wifi", "lifi")
    }
    for rat in ("5g", "wifi", "lifi"):
        frame[f"active_{rat}"] = (frame[f"traffic_{rat}"] > active_thresholds[rat]).astype(float)

    scalers = {
        "wifi_signal": MinMax.fit(train["wifi_signal_mean"].to_numpy()),
        "lifi_signal": MinMax.fit(train["lifi_signal"].to_numpy()),
        "load": MinMax.fit(train["total_wireless_traffic"].to_numpy()),
        "inactivity": MinMax.fit(train["wifi_inactivity_mean"].to_numpy()),
        "fluctuation": MinMax.fit(train["traffic_fluctuation"].to_numpy()),
        "rolling_mean": MinMax.fit(train["traffic_rolling_mean"].to_numpy()),
    }
    frame["wifi_signal_quality"] = scalers["wifi_signal"].transform(frame["wifi_signal_mean"])
    frame["lifi_signal_quality"] = scalers["lifi_signal"].transform(frame["lifi_signal"])
    frame["signal_quality"] = 0.7 * frame["wifi_signal_quality"] + 0.3 * frame["lifi_signal_quality"]
    frame["wireless_load_score"] = scalers["load"].transform(frame["total_wireless_traffic"])
    frame["inactivity_risk"] = scalers["inactivity"].transform(frame["wifi_inactivity_mean"])
    frame["traffic_fluctuation_score"] = scalers["fluctuation"].transform(frame["traffic_fluctuation"])
    frame["traffic_rolling_mean_score"] = scalers["rolling_mean"].transform(frame["traffic_rolling_mean"])
    for column in [
        "wifi_signal_quality", "lifi_signal_quality", "signal_quality", "wireless_load_score",
        "inactivity_risk", "traffic_fluctuation_score", "traffic_rolling_mean_score",
    ]:
        frame[column] = frame[column].clip(0, 1)
    frame["access_diversity_score"] = frame[["active_5g", "active_wifi", "active_lifi"]].sum(axis=1) / 3.0
    frame["link_stability_score"] = (
        0.5 * frame["signal_quality"]
        + 0.3 * (1.0 - frame["traffic_fluctuation_score"])
        + 0.2 * (1.0 - frame["inactivity_risk"])
    ).clip(0, 1)
    logit = (
        2.0 * frame["wireless_load_score"]
        + 1.5 * frame["inactivity_risk"]
        + frame["traffic_fluctuation_score"]
        - 1.5 * frame["link_stability_score"]
        - 0.8 * frame["access_diversity_score"]
    )
    frame["congestion_risk"] = 1.0 / (1.0 + np.exp(-logit))
    frame["semantic_confidence"] = (1.0 - frame["traffic_fluctuation_score"]).clip(0, 1)

    params = {
        "active_thresholds": active_thresholds,
        "minmax": {name: vars(value) for name, value in scalers.items()},
    }
    return frame, params


class BottleneckRegressor:
    """Small supervised encoder-decoder trained with mini-batch Adam."""

    def __init__(
        self,
        input_dim: int,
        output_dim: int,
        encoder_hidden: list[int],
        latent_dim: int,
        decoder_hidden: list[int],
        noise_sigma: float,
        seed: int,
    ) -> None:
        self.encoder_hidden = encoder_hidden
        self.latent_dim = latent_dim
        self.noise_sigma = noise_sigma
        self.seed = seed
        self.latent_layer = len(encoder_hidden)
        dimensions = [input_dim] + encoder_hidden + [latent_dim] + decoder_hidden + [output_dim]
        rng = np.random.default_rng(seed)
        self.weights = [
            rng.normal(0, math.sqrt(2.0 / dimensions[i]), size=(dimensions[i], dimensions[i + 1]))
            for i in range(len(dimensions) - 1)
        ]
        self.biases = [np.zeros(dimensions[i + 1], dtype=float) for i in range(len(dimensions) - 1)]

    def _forward(self, x: np.ndarray) -> tuple[list[np.ndarray], list[np.ndarray]]:
        activations = [x]
        preactivations = []
        for index, (weight, bias) in enumerate(zip(self.weights, self.biases)):
            z = activations[-1] @ weight + bias
            preactivations.append(z)
            is_linear = index == self.latent_layer or index == len(self.weights) - 1
            activations.append(z if is_linear else np.maximum(z, 0.0))
        return activations, preactivations

    def fit(
        self,
        x_train: np.ndarray,
        y_train: np.ndarray,
        x_val: np.ndarray,
        y_val: np.ndarray,
        max_epochs: int = 200,
        batch_size: int = 32,
        patience: int = 12,
        learning_rate: float = 1e-3,
    ) -> dict:
        rng = np.random.default_rng(self.seed)
        mw = [np.zeros_like(weight) for weight in self.weights]
        vw = [np.zeros_like(weight) for weight in self.weights]
        mb = [np.zeros_like(bias) for bias in self.biases]
        vb = [np.zeros_like(bias) for bias in self.biases]
        beta1, beta2, epsilon = 0.9, 0.999, 1e-8
        best_loss = float("inf")
        best_weights = None
        best_biases = None
        stale = 0
        step = 0
        history = []

        for epoch in range(max_epochs):
            order = rng.permutation(len(x_train))
            for start in range(0, len(order), batch_size):
                batch_indices = order[start:start + batch_size]
                xb = x_train[batch_indices].copy()
                if self.noise_sigma > 0:
                    xb += rng.normal(0, self.noise_sigma, size=xb.shape)
                yb = y_train[batch_indices]
                activations, preactivations = self._forward(xb)
                delta = 2.0 * (activations[-1] - yb) / (len(yb) * yb.shape[1])
                grad_w = [np.zeros_like(weight) for weight in self.weights]
                grad_b = [np.zeros_like(bias) for bias in self.biases]
                for layer in reversed(range(len(self.weights))):
                    grad_w[layer] = activations[layer].T @ delta
                    grad_b[layer] = delta.sum(axis=0)
                    if layer > 0:
                        delta = delta @ self.weights[layer].T
                        previous_layer = layer - 1
                        if previous_layer != self.latent_layer:
                            delta *= preactivations[previous_layer] > 0
                step += 1
                for layer in range(len(self.weights)):
                    mw[layer] = beta1 * mw[layer] + (1 - beta1) * grad_w[layer]
                    vw[layer] = beta2 * vw[layer] + (1 - beta2) * (grad_w[layer] ** 2)
                    mb[layer] = beta1 * mb[layer] + (1 - beta1) * grad_b[layer]
                    vb[layer] = beta2 * vb[layer] + (1 - beta2) * (grad_b[layer] ** 2)
                    mw_hat = mw[layer] / (1 - beta1 ** step)
                    vw_hat = vw[layer] / (1 - beta2 ** step)
                    mb_hat = mb[layer] / (1 - beta1 ** step)
                    vb_hat = vb[layer] / (1 - beta2 ** step)
                    self.weights[layer] -= learning_rate * mw_hat / (np.sqrt(vw_hat) + epsilon)
                    self.biases[layer] -= learning_rate * mb_hat / (np.sqrt(vb_hat) + epsilon)

            train_prediction = self.predict(x_train)
            val_prediction = self.predict(x_val)
            train_loss = float(np.mean((train_prediction - y_train) ** 2))
            val_loss = float(np.mean((val_prediction - y_val) ** 2))
            history.append({"epoch": epoch + 1, "train_loss": train_loss, "val_loss": val_loss})
            if val_loss < best_loss - 1e-8:
                best_loss = val_loss
                best_weights = [weight.copy() for weight in self.weights]
                best_biases = [bias.copy() for bias in self.biases]
                stale = 0
            else:
                stale += 1
                if stale >= patience:
                    break
        if best_weights is not None:
            self.weights = best_weights
            self.biases = best_biases
        return {
            "epochs": len(history),
            "best_val_loss": best_loss,
            "final_train_loss": history[-1]["train_loss"],
            "history": history,
        }

    def predict(self, x: np.ndarray) -> np.ndarray:
        return self._forward(np.asarray(x, dtype=float))[0][-1]

    def transform(self, x: np.ndarray) -> np.ndarray:
        activations, _ = self._forward(np.asarray(x, dtype=float))
        return activations[self.latent_layer + 1]


def fit_representation(
    name: str,
    x: np.ndarray,
    y: np.ndarray,
    splits: dict[str, np.ndarray],
    seed: int,
    encoder_hidden: list[int],
    latent_dim: int,
    noise_sigma: float,
) -> tuple[np.ndarray, np.ndarray, dict]:
    x_scaler = StandardScaler().fit(x[splits["train"]])
    y_scaler = StandardScaler().fit(y[splits["train"]])
    xs = x_scaler.transform(x)
    ys = y_scaler.transform(y)
    model = BottleneckRegressor(
        input_dim=x.shape[1],
        output_dim=y.shape[1],
        encoder_hidden=encoder_hidden,
        latent_dim=latent_dim,
        decoder_hidden=list(reversed(encoder_hidden)),
        noise_sigma=noise_sigma,
        seed=seed,
    )
    training = model.fit(
        xs[splits["train"]], ys[splits["train"]],
        xs[splits["validation"]], ys[splits["validation"]],
    )
    decoded = np.clip(y_scaler.inverse_transform(model.predict(xs)), 0, 1)
    latent = model.transform(xs)
    metadata = {
        "name": name,
        "seed": seed,
        "encoder_hidden": encoder_hidden,
        "latent_dim": latent_dim,
        "noise_sigma": noise_sigma,
        "epochs": training["epochs"],
        "best_val_loss": training["best_val_loss"],
        "final_train_loss": training["final_train_loss"],
    }
    return decoded, latent, metadata


def metric_row(y_true: np.ndarray, pred: np.ndarray, probability: np.ndarray | None, task: str) -> dict:
    row = {
        "accuracy": accuracy_score(y_true, pred),
        "balanced_accuracy": balanced_accuracy_score(y_true, pred),
        "macro_f1": f1_score(y_true, pred, average="macro", zero_division=0),
    }
    if task == "binary" and probability is not None and len(np.unique(y_true)) == 2:
        row["auroc"] = roc_auc_score(y_true, probability)
        row["auprc"] = average_precision_score(y_true, probability)
    else:
        row["auroc"] = np.nan
        row["auprc"] = np.nan
    return row


def evaluate_utility(
    method: str,
    features: np.ndarray,
    target: np.ndarray,
    splits: dict[str, np.ndarray],
    seed: int,
    task: str,
) -> tuple[dict, np.ndarray, dict]:
    train, test = splits["train"], splits["test"]
    if method == "Majority":
        values, counts = np.unique(target[train], return_counts=True)
        majority = values[np.argmax(counts)]
        pred = np.full(len(test), majority)
        probability = np.full(len(test), float(np.mean(target[train]))) if task == "binary" else None
    elif method == "StratifiedRandom":
        rng = np.random.default_rng(seed)
        values, counts = np.unique(target[train], return_counts=True)
        probabilities = counts / counts.sum()
        pred = rng.choice(values, size=len(test), p=probabilities)
        probability = np.full(len(test), probabilities[list(values).index(1)]) if task == "binary" and 1 in values else None
    else:
        model = Pipeline([
            ("scale", StandardScaler()),
            ("classifier", RandomForestClassifier(
                n_estimators=300, max_depth=8, random_state=seed,
                class_weight="balanced", n_jobs=-1,
            )),
        ])
        model.fit(features[train], target[train])
        pred = model.predict(features[test])
        probability = None
        if task == "binary" and len(model.named_steps["classifier"].classes_) == 2:
            classes = list(model.named_steps["classifier"].classes_)
            probability = model.predict_proba(features[test])[:, classes.index(1)]
    row = {"method": method, "seed": seed, "task": task, **metric_row(target[test], pred, probability, task)}
    details = classification_report(target[test], pred, output_dict=True, zero_division=0)
    return row, confusion_matrix(target[test], pred, labels=np.unique(target)), details


def attacker_estimators(seed: int) -> dict[str, Pipeline]:
    return {
        "LogisticRegression": Pipeline([
            ("scale", StandardScaler()),
            ("classifier", LogisticRegression(max_iter=1000, class_weight="balanced", random_state=seed)),
        ]),
        "RandomForest": Pipeline([
            ("scale", StandardScaler()),
            ("classifier", RandomForestClassifier(
                n_estimators=300, max_depth=8, class_weight="balanced", random_state=seed, n_jobs=-1,
            )),
        ]),
        "MLP": Pipeline([
            ("scale", StandardScaler()),
            ("classifier", MLPClassifier(
                hidden_layer_sizes=(32, 16), max_iter=300, early_stopping=True,
                random_state=seed, learning_rate_init=1e-3,
            )),
        ]),
        "GradientBoosting": Pipeline([
            ("scale", StandardScaler()),
            ("classifier", HistGradientBoostingClassifier(
                max_iter=200, max_depth=6, class_weight="balanced", random_state=seed,
            )),
        ]),
    }


def evaluate_privacy(
    representation: str,
    features: np.ndarray,
    raw_target: np.ndarray,
    target_name: str,
    splits: dict[str, np.ndarray],
    seed: int,
) -> list[dict]:
    train, test = splits["train"], splits["test"]
    encoder = LabelEncoder().fit(raw_target[train])
    known = np.isin(raw_target[test], encoder.classes_)
    train_target = encoder.transform(raw_target[train])
    test_target = encoder.transform(raw_target[test][known])
    rows = []
    for attacker_name, model in attacker_estimators(seed).items():
        model.fit(features[train], train_target)
        pred = model.predict(features[test][known])
        rows.append({
            "representation": representation,
            "attacker": attacker_name,
            "target": target_name,
            "seed": seed,
            "test_samples": int(known.sum()),
            "unseen_test_labels": int((~known).sum()),
            "accuracy": accuracy_score(test_target, pred),
            "balanced_accuracy": balanced_accuracy_score(test_target, pred),
            "macro_f1": f1_score(test_target, pred, average="macro", zero_division=0),
        })
    return rows


def add_privacy_baselines(raw_target: np.ndarray, target_name: str, splits: dict[str, np.ndarray], seed: int) -> list[dict]:
    train, test = splits["train"], splits["test"]
    values, counts = np.unique(raw_target[train], return_counts=True)
    majority = values[np.argmax(counts)]
    rng = np.random.default_rng(seed)
    random_pred = rng.choice(values, size=len(test), p=counts / counts.sum())
    results = []
    for name, pred in [("Majority", np.full(len(test), majority)), ("StratifiedRandom", random_pred)]:
        results.append({
            "representation": name,
            "attacker": "Baseline",
            "target": target_name,
            "seed": seed,
            "test_samples": len(test),
            "unseen_test_labels": int((~np.isin(raw_target[test], values)).sum()),
            "accuracy": accuracy_score(raw_target[test], pred),
            "balanced_accuracy": balanced_accuracy_score(raw_target[test], pred),
            "macro_f1": f1_score(raw_target[test], pred, average="macro", zero_division=0),
        })
    return results


def summarize(frame: pd.DataFrame, group_columns: list[str], metric_columns: list[str]) -> pd.DataFrame:
    records = []
    for keys, group in frame.groupby(group_columns, dropna=False):
        if not isinstance(keys, tuple):
            keys = (keys,)
        record = dict(zip(group_columns, keys))
        record["runs"] = len(group)
        for metric in metric_columns:
            values = pd.to_numeric(group[metric], errors="coerce").dropna()
            record[f"{metric}_mean"] = values.mean() if len(values) else np.nan
            record[f"{metric}_std"] = values.std(ddof=1) if len(values) > 1 else 0.0
            record[f"{metric}_ci95"] = 1.96 * values.std(ddof=1) / math.sqrt(len(values)) if len(values) > 1 else 0.0
        records.append(record)
    return pd.DataFrame(records)


def save_split_and_label_information(
    splits: dict[str, np.ndarray],
    times: np.ndarray,
    binary: np.ndarray,
    multiclass: np.ndarray,
    cpe: np.ndarray,
    rat: np.ndarray,
) -> None:
    split_rows = []
    label_rows = []
    for split_name, indices in splits.items():
        if split_name == "purged":
            continue
        split_rows.append({
            "split": split_name,
            "samples": len(indices),
            "start": str(times[indices[0]]),
            "end": str(times[indices[-1]]),
        })
        for target_name, target in [
            ("service_risk_next", binary), ("degradation_class_next", multiclass),
            ("dominant_cpe", cpe), ("dominant_rat", rat),
        ]:
            values, counts = np.unique(target[indices], return_counts=True)
            for value, count in zip(values, counts):
                label_rows.append({
                    "split": split_name, "target": target_name, "label": value,
                    "count": int(count), "fraction": float(count / len(indices)),
                })
    pd.DataFrame(split_rows).to_csv(E1_DIR / "temporal_split.csv", index=False)
    pd.DataFrame(label_rows).to_csv(E1_DIR / "label_distributions.csv", index=False)
    pd.DataFrame(label_rows).to_csv(E2_DIR / "label_distributions.csv", index=False)


def main() -> None:
    started = time.time()
    E1_DIR.mkdir(parents=True, exist_ok=True)
    E2_DIR.mkdir(parents=True, exist_ok=True)

    base = build_wireless_base()
    optical = build_optical_aligned(base["time"])
    sample_count = len(base) - 1
    splits = temporal_indices(sample_count)
    semantic_frame, preprocessing = derive_semantics(base, splits["train"])

    optical_feature_columns = [column for column in optical.columns if column not in {"time", "original_optical_timestamp"}]
    optical_features = optical[optical_feature_columns].to_numpy(dtype=float)
    q_threshold = float(optical.iloc[splits["train"] + 1]["q_factor"].quantile(0.15))
    ber_threshold = float(optical.iloc[splits["train"] + 1]["ber"].quantile(0.85))
    optical_risk = ((optical["q_factor"] < q_threshold) | (optical["ber"] > ber_threshold)).astype(int).to_numpy()
    wireless_risk = (
        (semantic_frame["congestion_risk"] > 0.65)
        | (semantic_frame["link_stability_score"] < 0.35)
        | (semantic_frame["access_diversity_score"] < 0.34)
    ).astype(int).to_numpy()
    service_risk = np.logical_or(optical_risk, wireless_risk).astype(int)
    degradation = np.select(
        [
            (optical_risk == 0) & (wireless_risk == 0),
            (optical_risk == 0) & (wireless_risk == 1),
            (optical_risk == 1) & (wireless_risk == 0),
        ],
        [0, 1, 2],
        default=3,
    ).astype(int)
    binary_target = service_risk[1:]
    multi_target = degradation[1:]
    current_times = semantic_frame["time"].to_numpy()[:-1]
    cpe_target = semantic_frame["dominant_cpe"].to_numpy()[:-1]
    rat_target = semantic_frame["dominant_rat"].to_numpy()[:-1]
    save_split_and_label_information(splits, current_times, binary_target, multi_target, cpe_target, rat_target)

    x = semantic_frame[WIRELESS_FEATURES].to_numpy(dtype=float)[:-1]
    y = semantic_frame[TARGET_COLUMNS].to_numpy(dtype=float)[:-1]
    confidence = semantic_frame[["semantic_confidence"]].to_numpy(dtype=float)[:-1]
    optical_current = optical_features[:-1]
    raw_private = semantic_frame[PRIVATE_FEATURES].to_numpy(dtype=float)[:-1]
    v1_message = semantic_frame[[
        "wireless_load_score", "link_stability_score", "access_diversity_score", "congestion_risk",
        "traffic_rolling_mean_score", "traffic_fluctuation_score", "signal_quality", "inactivity_risk",
    ]].to_numpy(dtype=float)[:-1]

    configurations = {
        "V2_8D": ([64, 32], 8, 0.0),
        "V3_3D_sigma0": ([32, 16], 3, 0.0),
        "V3_3D_sigma001": ([32, 16], 3, 0.01),
        "V3_3D_sigma005": ([32, 16], 3, 0.05),
        "V3_3D_sigma010": ([32, 16], 3, 0.10),
        "V3_8D_sigma005": ([32, 16], 8, 0.05),
    }
    utility_rows = []
    privacy_rows = []
    training_rows = []
    representative_details: dict[str, dict] = {"utility": {}, "privacy": {}}

    for seed in SEEDS:
        learned: dict[str, dict[str, np.ndarray]] = {}
        for name, (hidden, latent_dim, noise) in configurations.items():
            decoded, latent, metadata = fit_representation(
                name, x, y, splits, seed, hidden, latent_dim, noise
            )
            learned[name] = {"decoded": decoded, "latent": latent}
            training_rows.append(metadata)

        x_scaler = StandardScaler().fit(x[splits["train"]])
        x_scaled = x_scaler.transform(x)
        pca = PCA(n_components=3, random_state=seed).fit(x_scaled[splits["train"]])
        pca3 = pca.transform(x_scaled)
        random_projection = GaussianRandomProjection(n_components=3, random_state=seed).fit(x_scaled[splits["train"]])
        rp3 = random_projection.transform(x_scaled)

        utility_representations = {
            "Majority": np.zeros((sample_count, 1)),
            "StratifiedRandom": np.zeros((sample_count, 1)),
            "OpticalOnly": optical_current,
            "WirelessSemanticOnly_V3": np.column_stack([learned["V3_3D_sigma005"]["decoded"], confidence]),
            "RawWirelessPlusOptical": np.column_stack([x, optical_current]),
            "V1PlusOptical": np.column_stack([y, confidence, optical_current]),
            "V2PlusOptical": np.column_stack([learned["V2_8D"]["decoded"], confidence, optical_current]),
            "V3PlusOptical": np.column_stack([learned["V3_3D_sigma005"]["decoded"], confidence, optical_current]),
            "PCA3PlusOptical": np.column_stack([pca3, confidence, optical_current]),
            "V3NoNoisePlusOptical": np.column_stack([learned["V3_3D_sigma0"]["decoded"], confidence, optical_current]),
            "V3_8DPlusOptical": np.column_stack([learned["V3_8D_sigma005"]["decoded"], confidence, optical_current]),
        }
        for method, features in utility_representations.items():
            for task, target in [("binary", binary_target), ("4class", multi_target)]:
                row, matrix, details = evaluate_utility(method, features, target, splits, seed, task)
                utility_rows.append(row)
                if seed == 42:
                    representative_details["utility"][f"{method}__{task}"] = {
                        "confusion_matrix": matrix.tolist(), "classification_report": details,
                    }

        privacy_representations = {
            "RawPrivate": raw_private,
            "V1": np.column_stack([v1_message, confidence]),
            "V2": np.column_stack([learned["V2_8D"]["latent"], confidence]),
            "V3_sigma005": np.column_stack([learned["V3_3D_sigma005"]["latent"], confidence]),
            "PCA3": np.column_stack([pca3, confidence]),
            "RandomProjection3": np.column_stack([rp3, confidence]),
            "V3_sigma0": np.column_stack([learned["V3_3D_sigma0"]["latent"], confidence]),
            "V3_sigma001": np.column_stack([learned["V3_3D_sigma001"]["latent"], confidence]),
            "V3_sigma010": np.column_stack([learned["V3_3D_sigma010"]["latent"], confidence]),
            "V3_8D_sigma005": np.column_stack([learned["V3_8D_sigma005"]["latent"], confidence]),
        }
        for target_name, target in [("dominant_cpe", cpe_target), ("dominant_rat", rat_target)]:
            privacy_rows.extend(add_privacy_baselines(target, target_name, splits, seed))
            for representation, features in privacy_representations.items():
                privacy_rows.extend(evaluate_privacy(
                    representation, features, target, target_name, splits, seed
                ))

    utility = pd.DataFrame(utility_rows)
    privacy = pd.DataFrame(privacy_rows)
    training = pd.DataFrame(training_rows)
    utility.to_csv(E1_DIR / "utility_results_per_seed.csv", index=False)
    training.to_csv(E1_DIR / "encoder_training_per_seed.csv", index=False)
    utility_summary = summarize(
        utility, ["method", "task"], ["accuracy", "balanced_accuracy", "macro_f1", "auroc", "auprc"]
    )
    utility_summary.to_csv(E1_DIR / "utility_results_summary.csv", index=False)
    privacy.to_csv(E2_DIR / "privacy_results_per_seed.csv", index=False)
    privacy_summary = summarize(
        privacy, ["representation", "attacker", "target"], ["accuracy", "balanced_accuracy", "macro_f1"]
    )
    privacy_summary.to_csv(E2_DIR / "privacy_results_summary.csv", index=False)
    (E1_DIR / "representative_seed42_details.json").write_text(
        json.dumps(representative_details["utility"], indent=2), encoding="utf-8"
    )

    dimensions = pd.DataFrame([
        {"representation": "RawWireless", "numeric_dimensions": len(WIRELESS_FEATURES)},
        {"representation": "V1", "numeric_dimensions": 9},
        {"representation": "V2", "numeric_dimensions": 9},
        {"representation": "V3", "numeric_dimensions": 4},
        {"representation": "PCA3", "numeric_dimensions": 4},
    ])
    dimensions["float32_payload_bytes"] = dimensions["numeric_dimensions"] * 4
    dimensions["relative_to_raw"] = dimensions["float32_payload_bytes"] / (len(WIRELESS_FEATURES) * 4)
    dimensions.to_csv(E1_DIR / "representation_dimensions.csv", index=False)

    split_config = {
        "split": "chronological_60_20_20",
        "purge_gap_records": PURGE_GAP,
        "record_interval_seconds": 30,
        "seeds": SEEDS,
        "optical_alignment": "sequence_based_constructed_benchmark_due_to_non_overlapping_campaigns",
        "optical_risk_thresholds_fitted_on_training_target_times": {
            "q_factor_15th_percentile": q_threshold,
            "ber_85th_percentile": ber_threshold,
        },
        "semantic_preprocessing_fitted_on_training_current_times": preprocessing,
    }
    (E1_DIR / "experiment_config.json").write_text(json.dumps(split_config, indent=2), encoding="utf-8")
    (E2_DIR / "experiment_config.json").write_text(json.dumps({
        "split_source": "../E1_semantic_utility/experiment_config.json",
        "attackers": list(attacker_estimators(42).keys()),
        "seeds": SEEDS,
        "primary_privacy_target": "dominant_cpe",
        "diagnostic_target": "dominant_rat_extremely_imbalanced",
    }, indent=2), encoding="utf-8")

    provenance = {
        "python": sys.version,
        "platform": platform.platform(),
        "numpy": np.__version__, "pandas": pd.__version__, "scipy": scipy.__version__,
        "scikit_learn": sklearn.__version__, "joblib": joblib.__version__,
        "source_files": {
            "wireless_real_30s.csv": sha256(SOURCE_DIR / "wireless_real_30s.csv"),
            "voyager.csv": sha256(SOURCE_DIR / "voyager.csv"),
        },
        "runtime_seconds": time.time() - started,
        "neural_implementation": "NumPy mini-batch Adam supervised bottleneck encoder-decoder",
    }
    (E1_DIR / "provenance.json").write_text(json.dumps(provenance, indent=2), encoding="utf-8")
    (E2_DIR / "provenance.json").write_text(json.dumps(provenance, indent=2), encoding="utf-8")

    plot_utility(utility_summary)
    plot_privacy(privacy_summary)
    plot_tradeoff(utility_summary, privacy_summary)
    write_readmes(utility_summary, privacy_summary, provenance)


def plot_utility(summary: pd.DataFrame) -> None:
    data = summary[summary["task"] == "binary"].copy().sort_values("macro_f1_mean", ascending=False)
    fig, ax = plt.subplots(figsize=(11, 6))
    ax.barh(data["method"], data["macro_f1_mean"], xerr=data["macro_f1_ci95"], color="#3b82f6")
    ax.set_xlabel("Binary service-risk Macro-F1 (mean and 95% CI)")
    ax.set_xlim(0, 1)
    ax.grid(axis="x", alpha=0.25)
    fig.tight_layout()
    fig.savefig(E1_DIR / "binary_macro_f1.png", dpi=300)
    plt.close(fig)


def plot_privacy(summary: pd.DataFrame) -> None:
    data = summary[(summary["target"] == "dominant_cpe") & (summary["attacker"] == "RandomForest")].copy()
    data = data.sort_values("macro_f1_mean", ascending=True)
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(data["representation"], data["macro_f1_mean"], xerr=data["macro_f1_ci95"], color="#ef4444")
    ax.set_xlabel("CPE attacker Macro-F1 (lower is less leakage)")
    ax.set_xlim(0, 1)
    ax.grid(axis="x", alpha=0.25)
    fig.tight_layout()
    fig.savefig(E2_DIR / "cpe_random_forest_attack.png", dpi=300)
    plt.close(fig)


def plot_tradeoff(utility: pd.DataFrame, privacy: pd.DataFrame) -> None:
    mapping = {"V1PlusOptical": "V1", "V2PlusOptical": "V2", "V3PlusOptical": "V3_sigma005", "PCA3PlusOptical": "PCA3"}
    rows = []
    for utility_name, privacy_name in mapping.items():
        u = utility[(utility["method"] == utility_name) & (utility["task"] == "binary")]
        p = privacy[
            (privacy["representation"] == privacy_name)
            & (privacy["target"] == "dominant_cpe")
            & (privacy["attacker"] != "Baseline")
        ]
        if len(u) and len(p):
            strongest = p.sort_values("macro_f1_mean", ascending=False).iloc[0]
            rows.append({
                "method": utility_name.replace("PlusOptical", ""),
                "utility": float(u.iloc[0]["macro_f1_mean"]),
                "privacy_leakage": float(strongest["macro_f1_mean"]),
                "strongest_attacker": strongest["attacker"],
            })
    tradeoff = pd.DataFrame(rows)
    tradeoff.to_csv(E2_DIR / "privacy_utility_tradeoff.csv", index=False)
    fig, ax = plt.subplots(figsize=(7, 6))
    for row in tradeoff.itertuples(index=False):
        ax.scatter(row.privacy_leakage, row.utility, s=90)
        ax.annotate(row.method, (row.privacy_leakage, row.utility), xytext=(5, 5), textcoords="offset points")
    ax.set_xlabel("Strongest CPE attacker Macro-F1 (lower is better)")
    ax.set_ylabel("Binary utility Macro-F1 (higher is better)")
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(E2_DIR / "privacy_utility_tradeoff.png", dpi=300)
    plt.close(fig)


def write_readmes(utility: pd.DataFrame, privacy: pd.DataFrame, provenance: dict) -> None:
    top_utility = utility[utility["task"] == "binary"].sort_values("macro_f1_mean", ascending=False).head(5)
    e1_text = """# E1: Leakage-free temporal semantic-utility experiment

This directory is produced by `MajorRevision/run_e1_e2.py`.

Important interpretation: the optical and wireless campaigns do not overlap in time. The sequence mapping is retained only as a constructed data-interoperability benchmark; it is not a contemporaneous end-to-end measurement.

All scalers, semantic thresholds, optical risk thresholds, encoders and downstream models are fitted after the chronological split. Ten records are purged at each boundary. The four-class result is exploratory if the final test block contains too few samples of class 3.

## Top binary results

""" + top_utility.to_markdown(index=False) + f"\n\nRuntime: {provenance['runtime_seconds']:.1f} s.\n"
    (E1_DIR / "README.md").write_text(e1_text, encoding="utf-8")

    cpe = privacy[(privacy["target"] == "dominant_cpe") & (privacy["attacker"] != "Baseline")]
    strongest = cpe.sort_values("macro_f1_mean", ascending=False).groupby("representation", as_index=False).first()
    e2_text = """# E2: Multi-attacker privacy experiment

This directory is produced by `MajorRevision/run_e1_e2.py` using the same chronological split as E1.

Dominant CPE is the primary privacy target. Dominant RAT is diagnostic only because Wi-Fi accounts for approximately 98.6% of all records in the full dataset. Accuracy on RAT must not be interpreted without the majority baseline.

The table below reports the strongest observed CPE attacker for each representation; lower Macro-F1 means less observed leakage.

""" + strongest[["representation", "attacker", "macro_f1_mean", "macro_f1_ci95"]].to_markdown(index=False) + "\n"
    (E2_DIR / "README.md").write_text(e2_text, encoding="utf-8")


if __name__ == "__main__":
    main()
