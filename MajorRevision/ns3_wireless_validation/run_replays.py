#!/usr/bin/env python3
"""Run the W1 representative, repeatability, and seed-sensitivity checks.

The replay executables are compiled from the archived generated.cc files with
the existing ns-3.44 installation.  All generated sources, binaries, logs,
and simulator outputs are placed below W1_NS3_VALIDATION; no ns-3 source or
build tree is modified.
"""

from __future__ import annotations

import csv
import json
import math
import shutil
import subprocess
import zipfile
from collections import defaultdict
from pathlib import Path
from typing import Any

import archive_audit as audit


WORKSPACE = Path("/home/ubuntu/Desktop/LLM Driven wireless environment generation")
PROJECT = WORKSPACE / "LLM-Driven-Multi-Agent-Optical-Digital-Twin-for-Automated-Data-Generation"
SWEEP = PROJECT / "NS3_Wireless_Hybrid_ParamSweep"
ARCHIVE = SWEEP / "artifacts.zip"
OUT = WORKSPACE / "W1_NS3_VALIDATION"
REPLAYS = OUT / "replays"
NS3_ROOT = Path("/home/ubuntu/Desktop/ns-allinone-3.44/ns-3.44")
NS3_BUILD = NS3_ROOT / "build"
COMPILER = Path("/usr/bin/c++")

SELECTED = {
    "low_load_low_mobility": (2.0, 0.5, 50.0, 1),
    "medium_load_high_mobility": (10.0, 3.0, 100.0, 2),
    "high_load_high_mobility": (20.0, 3.0, 100.0, 3),
}

APP_FLOW_IDS = tuple(range(5, 14))
METRICS = ("throughput_mbps", "packet_loss_ratio", "mean_delay_ms", "mean_jitter_ms")
REPLAY_METRICS = ("throughput_mbps", "packet_loss_ratio", "mean_delay_ms", "mean_jitter_ms")


def read_archive_roots() -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    with zipfile.ZipFile(ARCHIVE) as zf:
        for name in zf.namelist():
            if not name.endswith("/scenario.json"):
                continue
            root = name.split("/", 1)[0]
            scenario = json.loads(zf.read(name))
            expansion = scenario["expansion_parameters"]
            key = (
                float(expansion["offered_load_mbps"]),
                float(expansion["mobility_speed_mps"]),
                float(expansion["lifi_rate_mbps"]),
                int(scenario["random_seed"]),
            )
            result[root] = {"scenario": scenario, "key": key}
    return result


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields: list[str] = []
    for row in rows:
        for field in row:
            if field not in fields:
                fields.append(field)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def selected_roots(roots: dict[str, dict[str, Any]]) -> dict[str, str]:
    result: dict[str, str] = {}
    for label, wanted in SELECTED.items():
        matches = [root for root, info in roots.items() if info["key"] == wanted]
        if len(matches) != 1:
            raise RuntimeError(f"Expected one archive root for {label}={wanted}, got {matches}")
        result[label] = matches[0]
    return result


def compile_command(source: Path, binary: Path) -> list[str]:
    defines = [
        "-DHAVE_LIBXML2",
        "-DHAVE_PACKET_H",
        "-DNS3_ASSERT_ENABLE",
        "-DNS3_BUILD_PROFILE_DEBUG",
        "-DNS3_LOG_ENABLE",
        f'-DPROJECT_SOURCE_PATH="{NS3_ROOT}"',
        f'-DRAW_SOCK_CREATOR="{NS3_BUILD}/src/fd-net-device/ns3.44-raw-sock-creator-default"',
        f'-DTAP_CREATOR="{NS3_BUILD}/src/tap-bridge/ns3.44-tap-creator-default"',
        f'-DTAP_DEV_CREATOR="{NS3_BUILD}/src/fd-net-device/ns3.44-tap-device-creator-default"',
        "-D__LINUX__",
    ]
    includes = [f"-I{NS3_BUILD}/include", "-I/usr/include/libxml2"]
    flags = ["-Os", "-g", "-DNDEBUG", "-std=c++20", "-fPIE", "-fno-semantic-interposition", "-Wall", "-Wpedantic"]
    library_names = [
        "zigbee", "topology-read", "tap-bridge", "sixlowpan", "point-to-point-layout",
        "olsr", "nix-vector-routing", "netanim", "lte", "lr-wpan", "flow-monitor",
        "fd-net-device", "dsr", "dsdv", "csma-layout", "csma", "config-store",
        "buildings", "aodv",
    ]
    library_names_after_as_needed = [
        "wimax", "uan", "virtual-net-device", "mesh", "point-to-point", "wifi",
        "spectrum", "propagation", "mobility", "antenna", "energy", "internet-apps",
        "applications", "internet", "traffic-control", "bridge", "network", "stats", "core",
    ]
    libs = [f"{NS3_BUILD}/lib/libns3.44-{name}-default.so" for name in library_names]
    libs_after = [f"{NS3_BUILD}/lib/libns3.44-{name}-default.so" for name in library_names_after_as_needed]
    return [
        str(COMPILER), *defines, *includes, *flags, str(source), "-o", str(binary),
        f"-L{NS3_BUILD}/lib", f"-Wl,-rpath,{NS3_BUILD}/lib", "-Wl,--no-as-needed",
        *libs, "-Wl,--as-needed", *libs_after, "-Wl,--no-as-needed",
        "/usr/lib/x86_64-linux-gnu/libxml2.so", "-Wl,--as-needed",
    ]


def compile_source(source: Path, binary: Path, log_path: Path) -> dict[str, Any]:
    command = compile_command(source, binary)
    result = subprocess.run(command, cwd=NS3_ROOT, text=True, capture_output=True, check=False)
    log_path.write_text(
        "COMMAND\n" + " ".join(command) + "\n\nSTDOUT\n" + result.stdout +
        "\nSTDERR\n" + result.stderr,
        encoding="utf-8",
    )
    return {"command": command, "returncode": result.returncode, "stdout": result.stdout, "stderr": result.stderr}


def run_binary(binary: Path, output_dir: Path, key: tuple[float, float, float, int], log_path: Path) -> dict[str, Any]:
    load, speed, lifi_rate, seed = key
    output_dir.mkdir(parents=True, exist_ok=True)
    # ns-3's CommandLine implementation in this build mishandles an absolute
    # outputDir containing spaces.  Run from the workspace and pass a relative
    # path; the resulting directory is still the exact absolute workspace path.
    output_arg = output_dir.relative_to(WORKSPACE)
    command = [
        str(binary),
        f"--outputDir={output_arg}",
        "--simTime=10.0",
        f"--seed={seed}",
        f"--offeredLoadMbps={load:g}",
        "--packetSize=1024",
        f"--mobilitySpeed={speed:g}",
        f"--lifiRateMbps={lifi_rate:g}",
    ]
    result = subprocess.run(command, cwd=WORKSPACE, text=True, capture_output=True, check=False)
    log_path.write_text(
        "COMMAND\n" + " ".join(command) + "\n\nSTDOUT\n" + result.stdout +
        "\nSTDERR\n" + result.stderr,
        encoding="utf-8",
    )
    return {"command": command, "returncode": result.returncode, "stdout": result.stdout, "stderr": result.stderr}


def parse_fresh(output_dir: Path) -> list[dict[str, Any]]:
    xml_path = output_dir / "flowmon.xml"
    if not xml_path.exists():
        raise RuntimeError(f"No FlowMonitor output at {xml_path}")
    audit.CURRENT_SIM_TIME = 10.0
    rows, _mapping = audit.parse_flowmon(xml_path.read_text(encoding="utf-8"))
    return [row for row in rows if row["is_application"]]


def row_metrics(row: dict[str, Any]) -> dict[str, float]:
    loss = row["lost_packets"] / row["tx_packets"] if row["tx_packets"] else 0.0
    return {
        "throughput_mbps": float(row["throughput_mbps"]),
        "packet_loss_ratio": float(loss),
        "mean_delay_ms": float(row["mean_delay_ms"]),
        "mean_jitter_ms": float(row["mean_jitter_ms"]),
    }


def numeric(value: Any) -> float:
    if value is None or value == "":
        return float("nan")
    return float(value)


def make_archived_rows() -> dict[tuple[str, int], dict[str, Any]]:
    rows = read_csv(OUT / "flowmonitor_recomputed.csv")
    return {
        (row["run_id"], int(row["flow_id"])): row
        for row in rows
        if row["is_application"] == "True"
    }


def replay_audit(roots: dict[str, dict[str, Any]], selected: dict[str, str]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    archived = make_archived_rows()
    rows: list[dict[str, Any]] = []
    run_info: dict[str, Any] = {}
    with zipfile.ZipFile(ARCHIVE) as zf:
        for label, root in selected.items():
            info = roots[root]
            run_dir = REPLAYS / label
            if run_dir.exists():
                shutil.rmtree(run_dir)
            run_dir.mkdir(parents=True)
            source_path = run_dir / "archived_generated.cc"
            source_path.write_bytes(zf.read(f"{root}/generated.cc"))
            scenario_path = run_dir / "archived_scenario.json"
            scenario_path.write_bytes(zf.read(f"{root}/scenario.json"))
            binary = run_dir / "archived_generated_rebuilt"
            compile_info = compile_source(source_path, binary, run_dir / "compile.log")
            key = info["key"]
            sim_output = run_dir / "fresh_results"
            run_info[label] = {
                "run_id": root,
                "key": list(key),
                "compile_returncode": compile_info["returncode"],
                "binary": str(binary),
                "run_command": None,
                "run_returncode": None,
                "application_flow_count": 0,
            }
            if compile_info["returncode"] != 0:
                continue
            run_info[label]["run"] = run_binary(binary, sim_output, key, run_dir / "run.log")
            run_info[label]["run_command"] = run_info[label]["run"]["command"]
            run_info[label]["run_returncode"] = run_info[label]["run"]["returncode"]
            if run_info[label]["run_returncode"] != 0:
                continue
            fresh = {row["flow_id"]: row for row in parse_fresh(sim_output)}
            run_info[label]["application_flow_count"] = len(fresh)
            for flow_id in APP_FLOW_IDS:
                old = archived[(root, flow_id)]
                new = fresh.get(flow_id)
                if new is None:
                    rows.append({
                        "replay_label": label, "run_id": root, "flow_id": flow_id,
                        "access_type": old["access_type"], "cpe": old["cpe"],
                        "structural_status": "MISSING_REPLAY_FLOW",
                    })
                    continue
                oldm = {
                    "throughput_mbps": numeric(old["throughput_mbps"]),
                    "packet_loss_ratio": numeric(old["flowmonitor_packet_loss_ratio"]),
                    "mean_delay_ms": numeric(old["mean_delay_ms"]),
                    "mean_jitter_ms": numeric(old["mean_jitter_ms"]),
                }
                newm = row_metrics(new)
                out = {
                    "replay_label": label,
                    "run_id": root,
                    "flow_id": flow_id,
                    "access_type": new["access_type"],
                    "cpe": new["cpe"],
                    "structural_status": "PRESENT",
                    "archived_tx_packets": int(old["tx_packets"]),
                    "replay_tx_packets": new["tx_packets"],
                    "archived_rx_packets": int(old["rx_packets"]),
                    "replay_rx_packets": new["rx_packets"],
                    "archived_flowmonitor_lost_packets": int(old["lost_packets"]),
                    "replay_flowmonitor_lost_packets": new["lost_packets"],
                }
                for metric in REPLAY_METRICS:
                    out[f"archived_{metric}"] = oldm[metric]
                    out[f"replay_{metric}"] = newm[metric]
                    out[f"delta_{metric}"] = newm[metric] - oldm[metric]
                    out[f"abs_delta_{metric}"] = abs(newm[metric] - oldm[metric])
                rows.append(out)
    return rows, run_info


def repeatability_audit(roots: dict[str, dict[str, Any]], selected: dict[str, str]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    label = "medium_load_high_mobility"
    root = selected[label]
    key = roots[root]["key"]
    source_dir = REPLAYS / label
    binary = source_dir / "archived_generated_rebuilt"
    repeat_dir = source_dir / "same_seed_repeat"
    if repeat_dir.exists():
        shutil.rmtree(repeat_dir)
    first_dir = repeat_dir / "run_1"
    second_dir = repeat_dir / "run_2"
    first = run_binary(binary, first_dir, key, repeat_dir / "run_1.log")
    second = run_binary(binary, second_dir, key, repeat_dir / "run_2.log")
    rows: list[dict[str, Any]] = []
    info: dict[str, Any] = {
        "run_id": root,
        "key": list(key),
        "run_1_returncode": first["returncode"],
        "run_2_returncode": second["returncode"],
        "run_1_command": first["command"],
        "run_2_command": second["command"],
    }
    if first["returncode"] != 0 or second["returncode"] != 0:
        return rows, info
    a = {row["flow_id"]: row for row in parse_fresh(first_dir)}
    b = {row["flow_id"]: row for row in parse_fresh(second_dir)}
    info["run_1_application_flow_count"] = len(a)
    info["run_2_application_flow_count"] = len(b)
    for flow_id in APP_FLOW_IDS:
        row_a = a.get(flow_id)
        row_b = b.get(flow_id)
        out: dict[str, Any] = {"run_id": root, "flow_id": flow_id, "structural_status": "PRESENT" if row_a and row_b else "MISSING"}
        if row_a and row_b:
            ma = row_metrics(row_a)
            mb = row_metrics(row_b)
            out.update({"access_type": row_a["access_type"], "cpe": row_a["cpe"], "tx_packets_run_1": row_a["tx_packets"], "tx_packets_run_2": row_b["tx_packets"], "rx_packets_run_1": row_a["rx_packets"], "rx_packets_run_2": row_b["rx_packets"]})
            for metric in REPLAY_METRICS:
                out[f"run_1_{metric}"] = ma[metric]
                out[f"run_2_{metric}"] = mb[metric]
                out[f"abs_delta_{metric}"] = abs(ma[metric] - mb[metric])
                out[f"exact_{metric}"] = ma[metric] == mb[metric]
        rows.append(out)
    info["all_application_flows_present"] = all(row["structural_status"] == "PRESENT" for row in rows)
    info["max_abs_deltas"] = {metric: max((row.get(f"abs_delta_{metric}", float("nan")) for row in rows), default=float("nan")) for metric in REPLAY_METRICS}
    info["exact_metric_counts"] = {metric: sum(bool(row.get(f"exact_{metric}")) for row in rows) for metric in REPLAY_METRICS}
    return rows, info


def seed_sensitivity_audit(roots: dict[str, dict[str, Any]], selected: dict[str, str]) -> list[dict[str, Any]]:
    target = (10.0, 3.0, 100.0)
    selected_by_seed = {
        int(info["key"][3]): root
        for root, info in roots.items()
        if info["key"][:3] == target
    }
    archived = make_archived_rows()
    rows: list[dict[str, Any]] = []
    for access in ("LTE/EPC", "Wi-Fi", "LiFi-surrogate"):
        for metric in METRICS:
            seed_means: dict[int, float] = {}
            all_values: list[float] = []
            for seed, root in sorted(selected_by_seed.items()):
                values = []
                for flow_id in APP_FLOW_IDS:
                    old = archived[(root, flow_id)]
                    if old["access_type"] != access:
                        continue
                    if metric == "packet_loss_ratio":
                        value = numeric(old["flowmonitor_packet_loss_ratio"])
                    else:
                        value = numeric(old[metric])
                    values.append(value)
                    all_values.append(value)
                seed_means[seed] = math.fsum(values) / len(values) if values else float("nan")
            mean = math.fsum(all_values) / len(all_values)
            sd = math.sqrt(math.fsum((value - mean) ** 2 for value in all_values) / (len(all_values) - 1)) if len(all_values) > 1 else 0.0
            seed_mean_values = list(seed_means.values())
            seed_mean = math.fsum(seed_mean_values) / len(seed_mean_values)
            seed_sd = math.sqrt(math.fsum((value - seed_mean) ** 2 for value in seed_mean_values) / (len(seed_mean_values) - 1)) if len(seed_mean_values) > 1 else 0.0
            rows.append({
                "fixed_offered_load_mbps": target[0],
                "fixed_mobility_speed_mps": target[1],
                "fixed_lifi_rate_mbps": target[2],
                "access_type": access,
                "metric": metric,
                "n_application_flows": len(all_values),
                "all_flow_mean": mean,
                "all_flow_std": sd,
                "seed1_mean": seed_means.get(1),
                "seed2_mean": seed_means.get(2),
                "seed3_mean": seed_means.get(3),
                "seed_mean_mean": seed_mean,
                "seed_mean_std": seed_sd,
                "seed_min_mean": min(seed_mean_values),
                "seed_max_mean": max(seed_mean_values),
            })
    return rows


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    REPLAYS.mkdir(parents=True, exist_ok=True)
    roots = read_archive_roots()
    selected = selected_roots(roots)
    replay_rows, replay_info = replay_audit(roots, selected)
    repeat_rows, repeat_info = repeatability_audit(roots, selected)
    sensitivity_rows = seed_sensitivity_audit(roots, selected)
    write_csv(OUT / "replay_results.csv", replay_rows)
    write_csv(OUT / "repeatability.csv", repeat_rows)
    write_csv(OUT / "seed_sensitivity.csv", sensitivity_rows)
    write_json(OUT / "replay_execution_summary.json", {"selected_runs": selected, "replays": replay_info, "repeatability": repeat_info})

    replay_status = []
    for label, info in replay_info.items():
        replay_status.append({
            "label": label,
            "run_id": info["run_id"],
            "compile_returncode": info["compile_returncode"],
            "run_returncode": info["run_returncode"],
            "application_flow_count": info["application_flow_count"],
        })
    print(json.dumps({"selected": selected, "replays": replay_status, "repeatability": repeat_info}, indent=2))


if __name__ == "__main__":
    main()
