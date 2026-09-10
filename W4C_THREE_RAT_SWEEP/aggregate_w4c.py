#!/usr/bin/env python3
"""Aggregate and structurally audit the frozen W4C 48-run dataset."""

from __future__ import annotations

import csv
import json
import math
import statistics
import xml.etree.ElementTree as ET
from collections import defaultdict
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent
RUNS = ROOT / "runs"
EVIDENCE = ROOT / "analysis"
EVIDENCE.mkdir(parents=True, exist_ok=True)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as stream:
        return list(csv.DictReader(stream))


def write_csv(path: Path, fields: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def config_values(path: Path) -> dict[str, str]:
    return {row["key"]: row["value"] for row in read_csv(path)}


def mean_std(values: list[float]) -> tuple[float, float]:
    return statistics.mean(values), statistics.stdev(values) if len(values) > 1 else 0.0


def raw_flow_count(path: Path) -> int:
    root = ET.parse(path).getroot()
    return len(root.findall("./Ipv4FlowClassifier/Flow"))


def finite(row: dict[str, str], fields: list[str]) -> bool:
    return all(math.isfinite(float(row[field])) for field in fields)


def main() -> int:
    run_dirs = sorted(path for path in RUNS.iterdir() if path.is_dir())
    application_rows: list[dict[str, object]] = []
    physical_rows: list[dict[str, object]] = []
    structural_rows: list[dict[str, object]] = []
    raw_flow_total = 0
    raw_required_kpi = ["throughput_mbps", "mean_delay_ms", "mean_jitter_ms", "flowmonitor_loss_ratio"]
    required_kpi = ["throughput_mbps", "mean_delay_ms", "mean_jitter_ms", "FlowMonitor_reported_loss_ratio"]
    for run_dir in run_dirs:
        cfg = config_values(run_dir / "run_config.csv")
        kpi = read_csv(run_dir / "kpi.csv")
        metadata = read_csv(run_dir / "scenario_metadata.csv")
        mapping = read_csv(run_dir / "flow_mapping.csv")
        optical = read_csv(run_dir / "optical_state.csv")
        raw_count = raw_flow_count(run_dir / "flowmon.xml")
        raw_flow_total += raw_count
        run_id = run_dir.name
        map_by_flow = {row["flow_id"]: row for row in mapping}
        optical_by_cpe: dict[str, list[dict[str, str]]] = defaultdict(list)
        for row in optical:
            optical_by_cpe[row["cpe_id"]].append(row)
        for row in kpi:
            map_row = map_by_flow.get(row["flow_id"], {})
            cpe = row["cpe_id"]
            out = {
                "run_id": run_id,
                "seed": int(cfg["random_seed"]),
                "offered_load_mbps": float(cfg["offered_load"]),
                "mobility_speed_mps": float(cfg["mobility_speed"]),
                "lifi_fov_deg": float(cfg["lifi_receiver_fov_deg"]),
                "branch": row["branch"],
                "CPE": int(cpe),
                "FlowId": int(row["flow_id"]),
                "source_ip": row["source_ip"],
                "destination_ip": row["destination_ip"],
                "source_port": int(row["source_port"]),
                "destination_port": int(row["destination_port"]),
                "tx_packets": int(row["tx_packets"]),
                "rx_packets": int(row["rx_packets"]),
                "lost_packets": int(row["lost_packets"]),
                "FlowMonitor_lostPackets": int(row["lost_packets"]),
                "rx_bytes": int(row["rx_bytes"]),
                "first_tx_s": float(row["first_tx_s"]),
                "last_rx_s": float(row["last_rx_s"]),
                "duration_s": float(row["duration_s"]),
                "throughput_mbps": float(row["throughput_mbps"]),
                "mean_delay_ms": float(row["mean_delay_ms"]),
                "mean_jitter_ms": float(row["mean_jitter_ms"]),
                "FlowMonitor_reported_loss_ratio": float(row["flowmonitor_loss_ratio"]),
                "mapping_status": map_row.get("mapping_status", "MISSING"),
                "interface_route_status": map_row.get("interface_route_status", "MISSING"),
            }
            if row["branch"] == "LiFi":
                states = optical_by_cpe.get(cpe, [])
                numeric = {field: [float(state[field]) for state in states] for field in [
                    "distance_m", "h_los", "received_optical_power_w", "snr", "ber", "per"
                ]}
                physical = {
                    "run_id": run_id,
                    "seed": out["seed"],
                    "offered_load_mbps": out["offered_load_mbps"],
                    "mobility_speed_mps": out["mobility_speed_mps"],
                    "lifi_fov_deg": out["lifi_fov_deg"],
                    "CPE": int(cpe),
                    "optical_state_rows": len(states),
                    "in_fov_fraction": statistics.mean(int(state["in_fov"]) for state in states),
                    "zero_gain_fraction": statistics.mean(float(state["h_los"]) == 0.0 for state in states),
                    "distance_mean": statistics.mean(numeric["distance_m"]),
                    "distance_min": min(numeric["distance_m"]),
                    "distance_max": max(numeric["distance_m"]),
                    "H_LOS_mean": statistics.mean(numeric["h_los"]),
                    "received_power_mean": statistics.mean(numeric["received_optical_power_w"]),
                    "SNR_mean": statistics.mean(numeric["snr"]),
                    "SNR_min": min(numeric["snr"]),
                    "BER_mean": statistics.mean(numeric["ber"]),
                    "PER_mean": statistics.mean(numeric["per"]),
                }
                physical_rows.append(physical)
            application_rows.append(out)
        branches = defaultdict(int)
        for row in kpi:
            branches[row["branch"]] += 1
        key_rows = {(int(row["seed"]), float(row["offered_load_mbps"]), float(row["mobility_speed_mps"]), float(row["lifi_fov_deg"]), row["branch"], int(row["CPE"])) for row in application_rows if row["run_id"] == run_id}
        unique_flow_map = len({row["flow_id"] for row in mapping})
        structural_rows.append({
            "run_id": run_id,
            "seed": cfg["random_seed"],
            "offered_load_mbps": cfg["offered_load"],
            "mobility_speed_mps": cfg["mobility_speed"],
            "lifi_fov_deg": cfg["lifi_receiver_fov_deg"],
            "raw_flowmonitor_rows": raw_count,
            "application_rows": len(kpi),
            "metadata_rows": len(metadata),
            "mapping_rows": len(mapping),
            "unique_mapping_flow_ids": unique_flow_map,
            "NR_rows": branches["NR"],
            "WiFi80211ax_rows": branches["WiFi80211ax"],
            "LiFi_rows": branches["LiFi"],
            "unique_application_keys": len(key_rows),
            "all_required_kpis_finite": int(all(finite(row, raw_required_kpi) for row in kpi)),
            "all_mapping_status_match": int(all(row["mapping_status"] == "MATCHED" and row["interface_route_status"] == "PASS" for row in mapping)),
            "status": "PASS" if len(kpi) == 9 and len(metadata) == 9 and len(mapping) == 9 and all(branches[b] == 3 for b in ("NR", "WiFi80211ax", "LiFi")) and all(finite(row, raw_required_kpi) for row in kpi) and all(row["mapping_status"] == "MATCHED" and row["interface_route_status"] == "PASS" for row in mapping) else "FAIL",
        })

    app_fields = [
        "run_id", "seed", "offered_load_mbps", "mobility_speed_mps", "lifi_fov_deg", "branch", "CPE", "FlowId",
        "source_ip", "destination_ip", "source_port", "destination_port", "tx_packets", "rx_packets", "lost_packets",
        "FlowMonitor_lostPackets", "rx_bytes", "first_tx_s", "last_rx_s", "duration_s", "throughput_mbps", "mean_delay_ms",
        "mean_jitter_ms", "FlowMonitor_reported_loss_ratio", "mapping_status", "interface_route_status",
    ]
    write_csv(EVIDENCE / "final_application_flow_dataset.csv", app_fields, application_rows)
    physical_fields = [
        "run_id", "seed", "offered_load_mbps", "mobility_speed_mps", "lifi_fov_deg", "CPE", "optical_state_rows",
        "in_fov_fraction", "zero_gain_fraction", "distance_mean", "distance_min", "distance_max", "H_LOS_mean",
        "received_power_mean", "SNR_mean", "SNR_min", "BER_mean", "PER_mean",
    ]
    write_csv(EVIDENCE / "lifi_physical_summary.csv", physical_fields, physical_rows)
    structure_fields = list(structural_rows[0])
    write_csv(EVIDENCE / "sweep_structure.csv", structure_fields, structural_rows)
    # One row per frozen run configuration for a compact dataset-summary
    # artifact; the application-flow table remains separate and contains one
    # row per run × branch × CPE.
    write_csv(EVIDENCE / "final_dataset_summary.csv", structure_fields, structural_rows)

    # Aggregate CPEs within each run/branch first. The three seed-level run
    # summaries are then the replicates in this file.
    run_branch: dict[tuple[float, float, float, str, int], list[dict[str, object]]] = defaultdict(list)
    for row in application_rows:
        key = (float(row["offered_load_mbps"]), float(row["mobility_speed_mps"]), float(row["lifi_fov_deg"]), str(row["branch"]), int(row["seed"]))
        run_branch[key].append(row)
    run_branch_means = []
    for (load, speed, fov, branch, seed), rows in sorted(run_branch.items()):
        run_branch_means.append({
            "offered_load_mbps": load,
            "mobility_speed_mps": speed,
            "lifi_fov_deg": fov,
            "branch": branch,
            "seed": seed,
            "n_cpe": len(rows),
                **{field: statistics.mean(float(row[field]) for row in rows) for field in required_kpi},
        })
    grouped: dict[tuple[float, float, float, str], list[dict[str, object]]] = defaultdict(list)
    for row in run_branch_means:
        grouped[(row["offered_load_mbps"], row["mobility_speed_mps"], row["lifi_fov_deg"], row["branch"])].append(row)
    grouped_rows = []
    for key, rows in sorted(grouped.items()):
        load, speed, fov, branch = key
        result = {"offered_load_mbps": load, "mobility_speed_mps": speed, "lifi_fov_deg": fov, "branch": branch, "n_seed_runs": len(rows), "n_cpe_per_run": 3}
        for field in required_kpi:
            values = [float(row[field]) for row in rows]
            result[f"{field}_mean"] = statistics.mean(values)
            result[f"{field}_std_across_seeds"] = statistics.stdev(values) if len(values) > 1 else 0.0
        grouped_rows.append(result)
    grouped_fields = ["offered_load_mbps", "mobility_speed_mps", "lifi_fov_deg", "branch", "n_seed_runs", "n_cpe_per_run"]
    for field in required_kpi:
        grouped_fields += [f"{field}_mean", f"{field}_std_across_seeds"]
    write_csv(EVIDENCE / "grouped_kpi_summary.csv", grouped_fields, grouped_rows)

    physical_grouped: dict[tuple[float, float, float], list[dict[str, object]]] = defaultdict(list)
    for row in physical_rows:
        physical_grouped[(float(row["offered_load_mbps"]), float(row["mobility_speed_mps"]), float(row["lifi_fov_deg"]))].append(row)
    physical_grouped_rows = []
    physical_metrics = ["in_fov_fraction", "zero_gain_fraction", "distance_mean", "H_LOS_mean", "received_power_mean", "SNR_mean", "SNR_min", "BER_mean", "PER_mean"]
    for key, rows in sorted(physical_grouped.items()):
        load, speed, fov = key
        # Each seed/CPE is first averaged to one run, then seeds are used as
        # the replicate axis.
        by_seed: dict[str, list[dict[str, object]]] = defaultdict(list)
        for row in rows:
            by_seed[str(row["seed"])].append(row)
        seed_means = []
        for seed, seed_rows in by_seed.items():
            seed_means.append({metric: statistics.mean(float(row[metric]) for row in seed_rows) for metric in physical_metrics})
        result = {"offered_load_mbps": load, "mobility_speed_mps": speed, "lifi_fov_deg": fov, "n_seed_runs": len(seed_means)}
        for metric in physical_metrics:
            values = [row[metric] for row in seed_means]
            result[f"{metric}_mean"] = statistics.mean(values)
            result[f"{metric}_std_across_seeds"] = statistics.stdev(values) if len(values) > 1 else 0.0
        physical_grouped_rows.append(result)
    physical_grouped_fields = ["offered_load_mbps", "mobility_speed_mps", "lifi_fov_deg", "n_seed_runs"]
    for metric in physical_metrics:
        physical_grouped_fields += [f"{metric}_mean", f"{metric}_std_across_seeds"]
    write_csv(EVIDENCE / "lifi_physical_grouped_summary.csv", physical_grouped_fields, physical_grouped_rows)

    expected_config_keys = {
        (load, speed, fov, seed)
        for load in (2.0, 5.0, 10.0, 20.0)
        for speed in (0.5, 3.0)
        for fov in (40.0, 70.0)
        for seed in (1, 2, 3)
    }
    observed_config_keys = [
        (float(row["offered_load_mbps"]), float(row["mobility_speed_mps"]), float(row["lifi_fov_deg"]), int(row["seed"]))
        for row in structural_rows
    ]
    observed_config_counter = Counter(observed_config_keys)
    observed_config_set = set(observed_config_keys)
    missing_configurations = sorted(expected_config_keys - observed_config_set)
    extra_configurations = sorted(observed_config_set - expected_config_keys)
    duplicate_configuration_keys = sum(max(count - 1, 0) for count in observed_config_counter.values())

    summary = {
        "run_configurations_expected": 48,
        "run_configurations_observed": len(run_dirs),
        "raw_flowmonitor_rows_total": raw_flow_total,
        "raw_flowmonitor_rows_per_run": sorted(set(int(row["raw_flowmonitor_rows"]) for row in structural_rows)),
        "application_rows_expected": 432,
        "application_rows_observed": len(application_rows),
        "NR_rows": sum(row["branch"] == "NR" for row in application_rows),
        "WiFi80211ax_rows": sum(row["branch"] == "WiFi80211ax" for row in application_rows),
        "LiFi_rows": sum(row["branch"] == "LiFi" for row in application_rows),
        "all_run_structures_pass": all(row["status"] == "PASS" for row in structural_rows),
        "all_required_kpis_finite": all(row["all_required_kpis_finite"] for row in structural_rows),
        "all_mappings_pass": all(row["all_mapping_status_match"] for row in structural_rows),
        "duplicate_application_keys": len(application_rows) - len({(row["seed"], row["offered_load_mbps"], row["mobility_speed_mps"], row["lifi_fov_deg"], row["branch"], row["CPE"]) for row in application_rows}),
        "physical_rows_observed": len(physical_rows),
        "grouped_kpi_cells": len(grouped_rows),
        "expected_configuration_key_count": len(expected_config_keys),
        "missing_configurations": missing_configurations,
        "extra_configurations": extra_configurations,
        "duplicate_configuration_keys": duplicate_configuration_keys,
    }
    (EVIDENCE / "sweep_structure_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    (EVIDENCE / "sweep_structure_report.md").write_text(
        "# W4C structural dataset check\n\n"
        + f"Run configurations: **{summary['run_configurations_observed']}/48**. Application rows: **{summary['application_rows_observed']}/432**. Raw FlowMonitor rows: **{summary['raw_flowmonitor_rows_total']}** ({summary['raw_flowmonitor_rows_per_run']} per run).\n\n"
        + f"Branch rows: NR={summary['NR_rows']}, WiFi80211ax={summary['WiFi80211ax_rows']}, LiFi={summary['LiFi_rows']}. Duplicate application keys: {summary['duplicate_application_keys']}. Missing configuration keys: {len(summary['missing_configurations'])}; extra configuration keys: {len(summary['extra_configurations'])}; duplicate configuration keys: {summary['duplicate_configuration_keys']}. All per-run structure checks: **{'PASS' if summary['all_run_structures_pass'] else 'FAIL'}**. All required KPI values finite: **{'PASS' if summary['all_required_kpis_finite'] else 'FAIL'}**. All tuple/interface mappings: **{'PASS' if summary['all_mappings_pass'] else 'FAIL'}**.\n\n"
        "The application table contains one row per run × branch × CPE. Raw FlowMonitor XML rows include non-application EPC/control flows and are not mixed into the application table.\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2))
    return 0 if summary["run_configurations_observed"] == 48 and summary["application_rows_observed"] == 432 and summary["all_run_structures_pass"] and summary["duplicate_application_keys"] == 0 and not summary["missing_configurations"] and not summary["extra_configurations"] and summary["duplicate_configuration_keys"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
