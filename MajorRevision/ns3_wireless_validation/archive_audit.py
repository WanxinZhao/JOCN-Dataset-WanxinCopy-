#!/usr/bin/env python3
"""Independent read-only audit of the archived 48-run ns-3 sweep.

This script intentionally does not import the project's data_upload.py and
does not treat scenarios.csv as the KPI source of truth.  It parses the
archived FlowMonitor XML and recomputes the documented KPI equations using
only standard-library modules.
"""

from __future__ import annotations

import csv
import json
import math
import re
import statistics
import zipfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any
from xml.etree import ElementTree


WORKSPACE = Path("/home/ubuntu/Desktop/LLM Driven wireless environment generation")
PROJECT = WORKSPACE / "LLM-Driven-Multi-Agent-Optical-Digital-Twin-for-Automated-Data-Generation"
SWEEP = PROJECT / "NS3_Wireless_Hybrid_ParamSweep"
ARCHIVE = SWEEP / "artifacts.zip"
SCENARIOS_CSV = SWEEP / "scenarios.csv"
OUT = WORKSPACE / "W1_NS3_VALIDATION"

APPLICATION_FLOW_IDS = tuple(range(5, 14))
APPLICATION_FLOW_COUNT = 9
RAW_FLOW_COUNT = 13
KPI_METRICS = (
    "tx_packets",
    "rx_packets",
    "lost_packets",
    "throughput_mbps",
    "mean_delay_ms",
    "mean_jitter_ms",
)


def number(value: Any) -> float:
    if value is None or value == "":
        return float("nan")
    return float(value)


def integer(value: Any) -> int:
    return int(round(number(value)))


def finite(value: float) -> bool:
    return math.isfinite(value)


def clean_json(value: Any) -> Any:
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return None
    if isinstance(value, dict):
        return {str(k): clean_json(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean_json(v) for v in value]
    return value


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(clean_json(value), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_time(value: str) -> float:
    """Parse ns-3 XML time values such as +1.007e+09ns into seconds."""
    match = re.fullmatch(
        r"([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)(ns|us|ms|s)",
        value.strip(),
    )
    if not match:
        raise ValueError(f"Unsupported ns-3 time value: {value!r}")
    scale = {"ns": 1e-9, "us": 1e-6, "ms": 1e-3, "s": 1.0}[match.group(2)]
    return float(match.group(1)) * scale


def parse_source_defaults(source: str) -> dict[str, float]:
    patterns = {
        "simTime": r"double simTime = ([0-9.]+);",
        "seed": r"int seed = ([0-9]+);",
        "offeredLoadMbps": r"double offeredLoadMbps = ([0-9.]+);",
        "packetSize": r"uint32_t packetSize = ([0-9]+);",
        "mobilitySpeed": r"double mobilitySpeed = ([0-9.]+);",
        "lifiRateMbps": r"double lifiRateMbps = ([0-9.]+);",
    }
    result: dict[str, float] = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, source)
        result[key] = float(match.group(1)) if match else float("nan")
    return result


def xml_text(zf: zipfile.ZipFile, root: str, relative: str) -> str:
    return zf.read(f"{root}/{relative}").decode("utf-8", errors="replace")


def json_from_zip(zf: zipfile.ZipFile, root: str, relative: str) -> dict[str, Any]:
    return json.loads(xml_text(zf, root, relative))


def classifier_from_xml(root: ElementTree.Element) -> dict[int, dict[str, str]]:
    result: dict[int, dict[str, str]] = {}
    classifier = root.find("Ipv4FlowClassifier")
    if classifier is None:
        return result
    for item in classifier.findall("Flow"):
        result[int(item.attrib["flowId"])] = dict(item.attrib)
    return result


def application_mapping(classifier: dict[int, dict[str, str]]) -> dict[int, dict[str, Any]]:
    """Map application flows from XML classifier addresses/ports, not KPI CSV."""
    result: dict[int, dict[str, Any]] = {}
    for flow_id, item in classifier.items():
        if item.get("protocol") != "17" or item.get("destinationPort") != "9":
            continue
        source = item.get("sourceAddress", "")
        destination = item.get("destinationAddress", "")
        destination_octet = destination.rsplit(".", 1)[-1] if "." in destination else ""
        if source == "10.0.0.2" and destination.startswith("7.0.0."):
            access = "LTE/EPC"
        elif source == "192.168.1.1" and destination.startswith("192.168.2."):
            access = "Wi-Fi"
        elif source == "192.168.3.1" and destination.startswith("192.168.4."):
            access = "LiFi-surrogate"
        else:
            access = "unknown"
        cpe = {"2": "CPE1", "3": "CPE2", "4": "CPE3"}.get(destination_octet, "unknown")
        result[flow_id] = {
            "flow_id": flow_id,
            "access_type": access,
            "cpe": cpe,
            "source_address": source,
            "destination_address": destination,
            "source_port": integer(item.get("sourcePort")),
            "destination_port": integer(item.get("destinationPort")),
            "protocol": integer(item.get("protocol")),
            "is_application": access != "unknown" and cpe != "unknown",
        }
    return result


def parse_flowmon(xml_text_value: str) -> tuple[list[dict[str, Any]], dict[int, dict[str, Any]]]:
    root = ElementTree.fromstring(xml_text_value)
    classifier = classifier_from_xml(root)
    mapping = application_mapping(classifier)
    stats_parent = root.find("FlowStats")
    if stats_parent is None:
        raise ValueError("FlowMonitor XML has no FlowStats element")
    rows: list[dict[str, Any]] = []
    for item in stats_parent.findall("Flow"):
        attrs = item.attrib
        flow_id = integer(attrs["flowId"])
        tx_packets = integer(attrs["txPackets"])
        rx_packets = integer(attrs["rxPackets"])
        lost_packets = integer(attrs["lostPackets"])
        tx_bytes = integer(attrs["txBytes"])
        rx_bytes = integer(attrs["rxBytes"])
        first_tx = parse_time(attrs["timeFirstTxPacket"])
        first_rx = parse_time(attrs["timeFirstRxPacket"])
        last_tx = parse_time(attrs["timeLastTxPacket"])
        last_rx = parse_time(attrs["timeLastRxPacket"])
        delay_sum = parse_time(attrs["delaySum"])
        jitter_sum = parse_time(attrs["jitterSum"])
        duration_raw = last_rx - first_tx
        sim_time = CURRENT_SIM_TIME
        duration_used = duration_raw if duration_raw > 0 else ((sim_time - 1.0) if sim_time > 1.0 else sim_time)
        throughput = (rx_bytes * 8.0) / duration_used / 1e6
        mean_delay = delay_sum * 1000.0 / rx_packets if rx_packets > 0 else 0.0
        mean_jitter = jitter_sum * 1000.0 / (rx_packets - 1) if rx_packets > 1 else 0.0
        row = {
            "flow_id": flow_id,
            "tx_packets": tx_packets,
            "rx_packets": rx_packets,
            "lost_packets": lost_packets,
            "tx_bytes": tx_bytes,
            "rx_bytes": rx_bytes,
            "first_tx_time_s": first_tx,
            "first_rx_time_s": first_rx,
            "last_tx_time_s": last_tx,
            "last_rx_time_s": last_rx,
            "duration_raw_s": duration_raw,
            "duration_used_s": duration_used,
            "throughput_mbps": throughput,
            "mean_delay_ms": mean_delay,
            "mean_jitter_ms": mean_jitter,
            "tx_minus_rx": tx_packets - rx_packets,
            "accounting_gap": tx_packets - rx_packets - lost_packets,
        }
        row.update(mapping.get(flow_id, {
            "access_type": "infrastructure-or-unclassified",
            "cpe": "",
            "source_address": "",
            "destination_address": "",
            "source_port": "",
            "destination_port": "",
            "protocol": "",
            "is_application": False,
        }))
        rows.append(row)
    return rows, mapping


def kpi_rows_from_text(text: str) -> list[dict[str, Any]]:
    return list(csv.DictReader(text.splitlines()))


def compare_values(independent: float, archived: float) -> tuple[float, float | None]:
    absolute = abs(independent - archived)
    if archived == 0.0:
        relative = 0.0 if absolute == 0.0 else None
    else:
        relative = absolute / abs(archived)
    return absolute, relative


def metric_summary(rows: list[dict[str, Any]], metric: str, application_only: bool) -> dict[str, Any]:
    selected = [row for row in rows if (not application_only or row["is_application"])]
    errors = [row[f"{metric}_abs_error"] for row in selected]
    relatives = [row[f"{metric}_relative_error"] for row in selected if row[f"{metric}_relative_error"] is not None]
    exact = sum(1 for row in selected if row[f"{metric}_independent"] == row[f"{metric}_archived"])
    tolerance = 1e-6 if metric in {"tx_packets", "rx_packets", "lost_packets"} else 1e-4
    tol_matches = sum(1 for value in errors if value <= tolerance)
    return {
        "compared_records": len(selected),
        "exact_numeric_matches": exact,
        "within_tolerance_records": tol_matches,
        "tolerance": tolerance,
        "maximum_absolute_error": max(errors) if errors else None,
        "mean_absolute_error": statistics.fmean(errors) if errors else None,
        "median_absolute_error": statistics.median(errors) if errors else None,
        "maximum_relative_error_nonzero_reference": max(relatives) if relatives else None,
        "mean_relative_error_nonzero_reference": statistics.fmean(relatives) if relatives else None,
        "zero_reference_records": sum(1 for row in selected if row[f"{metric}_archived"] == 0.0),
    }


def run_key(scenario: dict[str, Any]) -> tuple[float, int, float, int, float, float]:
    expansion = scenario.get("expansion_parameters") or {}
    return (
        float(scenario["duration_s"]),
        int(scenario["random_seed"]),
        float(expansion["offered_load_mbps"]),
        int(expansion["packet_size_bytes"]),
        float(expansion["mobility_speed_mps"]),
        float(expansion["lifi_rate_mbps"]),
    )


def nearly_equal(a: Any, b: Any, tolerance: float = 1e-9) -> bool:
    try:
        return abs(float(a) - float(b)) <= tolerance
    except (TypeError, ValueError):
        return str(a) == str(b)


def load_dataset_rows() -> list[dict[str, Any]]:
    with SCENARIOS_CSV.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def archive_audit() -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    global CURRENT_SIM_TIME
    recomputed_rows: list[dict[str, Any]] = []
    comparison_rows: list[dict[str, Any]] = []
    run_records: list[dict[str, Any]] = []
    source_defaults_counter: Counter[tuple[tuple[str, float], ...]] = Counter()
    all_accounting = Counter()

    with zipfile.ZipFile(ARCHIVE) as zf:
        names = set(zf.namelist())
        roots = sorted({
            name.split("/", 1)[0]
            for name in names
            if name.endswith("/scenario.json") and "/" in name
        })
        for root in roots:
            scenario = json.loads(xml_text(zf, root, "scenario.json"))
            CURRENT_SIM_TIME = float(scenario["duration_s"])
            source = xml_text(zf, root, "generated.cc")
            defaults = parse_source_defaults(source)
            source_defaults_counter[tuple(sorted(defaults.items()))] += 1
            xml_rows, mapping = parse_flowmon(xml_text(zf, root, "results/flowmon.xml"))
            archived_kpi = kpi_rows_from_text(xml_text(zf, root, "results/kpi.csv"))
            kpi_by_flow = {integer(row["flow_id"]): row for row in archived_kpi}
            expansion = scenario.get("expansion_parameters") or {}
            source_key = {
                "simTime": float(scenario["duration_s"]),
                "seed": float(scenario["random_seed"]),
                "offeredLoadMbps": float(expansion["offered_load_mbps"]),
                "packetSize": float(expansion["packet_size_bytes"]),
                "mobilitySpeed": float(expansion["mobility_speed_mps"]),
                "lifiRateMbps": float(expansion["lifi_rate_mbps"]),
            }
            source_default_mismatches = [
                key for key, expected in source_key.items()
                if not nearly_equal(defaults.get(key), expected)
            ]
            for row in xml_rows:
                flow_id = row["flow_id"]
                archived = kpi_by_flow.get(flow_id)
                if archived is None:
                    continue
                output = {
                    "run_id": root,
                    "flow_id": flow_id,
                    "is_application": bool(row["is_application"]),
                    "access_type": row["access_type"],
                    "cpe": row["cpe"],
                    "source_address": row["source_address"],
                    "destination_address": row["destination_address"],
                    "source_port": row["source_port"],
                    "destination_port": row["destination_port"],
                    "tx_packets": row["tx_packets"],
                    "rx_packets": row["rx_packets"],
                    "lost_packets": row["lost_packets"],
                    "tx_bytes": row["tx_bytes"],
                    "rx_bytes": row["rx_bytes"],
                    "first_tx_time_s": row["first_tx_time_s"],
                    "first_rx_time_s": row["first_rx_time_s"],
                    "last_tx_time_s": row["last_tx_time_s"],
                    "last_rx_time_s": row["last_rx_time_s"],
                    "duration_raw_s": row["duration_raw_s"],
                    "duration_used_s": row["duration_used_s"],
                    "throughput_mbps": row["throughput_mbps"],
                    "mean_delay_ms": row["mean_delay_ms"],
                    "mean_jitter_ms": row["mean_jitter_ms"],
                    "tx_minus_rx": row["tx_minus_rx"],
                    "accounting_gap": row["accounting_gap"],
                    "flowmonitor_packet_loss_ratio": (
                        row["lost_packets"] / row["tx_packets"] if row["tx_packets"] > 0 else 0.0
                    ),
                    "terminal_unreceived_ratio": (
                        row["tx_minus_rx"] / row["tx_packets"] if row["tx_packets"] > 0 else 0.0
                    ),
                    "source_defaults_mismatches": "|".join(source_default_mismatches),
                }
                for metric in KPI_METRICS:
                    independent = float(row[metric])
                    archived_value = number(archived[metric])
                    absolute, relative = compare_values(independent, archived_value)
                    output[f"{metric}_independent"] = independent
                    output[f"{metric}_archived"] = archived_value
                    output[f"{metric}_abs_error"] = absolute
                    output[f"{metric}_relative_error"] = relative
                    comparison_rows.append({
                        "run_id": root,
                        "flow_id": flow_id,
                        "is_application": row["is_application"],
                        "access_type": row["access_type"],
                        "cpe": row["cpe"],
                        "metric": metric,
                        "independent_value": independent,
                        "archived_value": archived_value,
                        "absolute_error": absolute,
                        "relative_error": relative,
                        "exact_numeric_match": independent == archived_value,
                    })
                recomputed_rows.append(output)
                if row["is_application"]:
                    all_accounting["application_flows"] += 1
                    all_accounting["accounting_gap_nonzero"] += int(row["accounting_gap"] != 0)
                    all_accounting["tx_minus_rx_nonzero"] += int(row["tx_minus_rx"] != 0)
                    all_accounting["flowmonitor_lost_nonzero"] += int(row["lost_packets"] != 0)
                    all_accounting["rx_zero"] += int(row["rx_packets"] == 0)
            run_records.append({
                "run_id": root,
                "scenario_key": list(run_key(scenario)),
                "scenario_duration_s": scenario["duration_s"],
                "scenario_random_seed": scenario["random_seed"],
                "scenario_expansion_parameters": expansion,
                "generated_source_defaults": defaults,
                "generated_source_default_mismatches": source_default_mismatches,
                "generated_source_has_command_parameters": all(
                    key in source for key in (
                        'cmd.AddValue("simTime"',
                        'cmd.AddValue("seed"',
                        'cmd.AddValue("offeredLoadMbps"',
                        'cmd.AddValue("packetSize"',
                        'cmd.AddValue("mobilitySpeed"',
                        'cmd.AddValue("lifiRateMbps"',
                    )
                ),
                "flowmon_raw_flow_count": len(xml_rows),
                "flowmon_application_flow_count": sum(row["is_application"] for row in xml_rows),
                "kpi_row_count": len(archived_kpi),
                "flow_ids_in_flowmon": sorted(row["flow_id"] for row in xml_rows),
                "application_flow_ids_in_flowmon": sorted(
                    row["flow_id"] for row in xml_rows if row["is_application"]
                ),
                "classifier_application_mapping": mapping,
            })

    run_records.sort(key=lambda row: row["run_id"])
    summary = {
        "archive": str(ARCHIVE),
        "run_count": len(run_records),
        "raw_flow_rows": len(recomputed_rows),
        "application_flow_rows": sum(row["is_application"] for row in recomputed_rows),
        "expected_run_count": 48,
        "expected_raw_flow_rows": 48 * RAW_FLOW_COUNT,
        "expected_application_flow_rows": 48 * APPLICATION_FLOW_COUNT,
        "source_default_patterns": [
            {"count": count, "defaults": dict(items)}
            for items, count in source_defaults_counter.items()
        ],
        "packet_accounting": dict(all_accounting),
        "metrics": {
            metric: {
                "all_flow_rows": metric_summary(recomputed_rows, metric, False),
                "application_flow_rows": metric_summary(recomputed_rows, metric, True),
            }
            for metric in KPI_METRICS
        },
        "physical_sanity": {
            "nonfinite_recomputed_values": sum(
                1 for row in recomputed_rows
                for metric in ("throughput_mbps", "mean_delay_ms", "mean_jitter_ms")
                if not finite(float(row[metric]))
            ),
            "negative_recomputed_values": sum(
                1 for row in recomputed_rows
                for metric in ("throughput_mbps", "mean_delay_ms", "mean_jitter_ms")
                if finite(float(row[metric])) and float(row[metric]) < 0
            ),
            "negative_archived_values": sum(
                1 for row in recomputed_rows
                for metric in ("throughput_mbps", "mean_delay_ms", "mean_jitter_ms")
                if finite(float(row[f"{metric}_archived"])) and float(row[f"{metric}_archived"]) < 0
            ),
            "archived_flowmonitor_loss_ratio_outside_0_1": sum(
                1 for row in recomputed_rows
                if not 0.0 <= float(row["flowmonitor_packet_loss_ratio"]) <= 1.0
            ),
        },
        "run_records": run_records,
    }
    return recomputed_rows, comparison_rows, summary


def consistency_audit(
    recomputed_rows: list[dict[str, Any]],
    archive_summary: dict[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    dataset_rows = load_dataset_rows()
    by_run_flow = defaultdict(list)
    for row in dataset_rows:
        scenario_id = row["scenario_id"]
        if "-flow-" not in scenario_id:
            continue
        run_id, flow_token = scenario_id.rsplit("-flow-", 1)
        by_run_flow[(run_id, integer(flow_token))].append(row)
    recomputed_by_key = {(row["run_id"], row["flow_id"]): row for row in recomputed_rows}
    run_records = archive_summary["run_records"]
    run_by_id = {row["run_id"]: row for row in run_records}
    top_level_by_run: dict[str, list[str]] = {}
    source_default_by_run: dict[str, list[str]] = {}
    with zipfile.ZipFile(ARCHIVE) as zf:
        for run_id in sorted(run_by_id):
            scenario = json.loads(xml_text(zf, run_id, "scenario.json"))
            expansion = scenario["expansion_parameters"]
            top_level_issues: list[str] = []
            if scenario["traffic"]["data_rate"] != f"{float(expansion['offered_load_mbps']):g}Mbps":
                top_level_issues.append("scenario.traffic.data_rate_vs_expansion")
            if not nearly_equal(scenario["mobility"]["speed_mps"], expansion["mobility_speed_mps"]):
                top_level_issues.append("scenario.mobility.speed_mps_vs_expansion")
            if scenario["lifi"]["data_rate"] != f"{float(expansion['lifi_rate_mbps']):g}Mbps":
                top_level_issues.append("scenario.lifi.data_rate_vs_expansion")
            top_level_by_run[run_id] = top_level_issues
            source_default_by_run[run_id] = next(
                (record["generated_source_default_mismatches"] for record in run_records if record["run_id"] == run_id),
                [],
            )
    expected_keys = {(run_id, flow_id) for run_id in run_by_id for flow_id in APPLICATION_FLOW_IDS}
    observed_keys = set(by_run_flow)
    detail_rows: list[dict[str, Any]] = []
    issue_counts = Counter()
    for key in sorted(expected_keys | observed_keys):
        run_id, flow_id = key
        archive_row = recomputed_by_key.get(key)
        dataset_matches = by_run_flow.get(key, [])
        issues: list[str] = []
        if run_id not in run_by_id:
            issues.append("dataset_extra_run")
        if flow_id not in APPLICATION_FLOW_IDS:
            issues.append("non_application_flow_in_dataset")
        if archive_row is None:
            issues.append("missing_flowmon_or_kpi_row")
        if len(dataset_matches) == 0:
            issues.append("missing_scenarios_row")
        if len(dataset_matches) > 1:
            issues.append("duplicated_application_flow_key")
        row = dataset_matches[0] if dataset_matches else {}
        mapping = archive_row or {}
        expected_access = mapping.get("access_type", "")
        expected_cpe = mapping.get("cpe", "")
        if row and row.get("access_type") != expected_access:
            issues.append("access_mapping_mismatch")
        if row and row.get("cpe") != expected_cpe:
            issues.append("cpe_mapping_mismatch")
        if row and integer(row.get("flow_id")) != flow_id:
            issues.append("flow_id_mismatch")
        if row and archive_row:
            for metric in ("tx_packets", "rx_packets", "lost_packets", "throughput_mbps",
                           "mean_delay_ms", "mean_jitter_ms"):
                if not nearly_equal(row.get(metric), archive_row[f"{metric}_archived"], 1e-8):
                    issues.append(f"kpi_mismatch_{metric}")
        run = run_by_id.get(run_id, {})
        scenario_key = run.get("scenario_key", ["", "", "", "", "", ""])
        if row:
            expected_fields = {
                "duration_s": scenario_key[0],
                "random_seed": scenario_key[1],
                "offered_load_mbps": scenario_key[2],
                "packet_size_bytes": scenario_key[3],
                "mobility_speed_mps": scenario_key[4],
                "lifi_rate_mbps": scenario_key[5],
            }
            for field, expected in expected_fields.items():
                if not nearly_equal(row.get(field), expected):
                    issues.append(f"parameter_mismatch_{field}")
        for issue in issues:
            issue_counts[issue] += 1
        detail_rows.append({
            "run_id": run_id,
            "flow_id": flow_id,
            "expected_application_flow": flow_id in APPLICATION_FLOW_IDS and run_id in run_by_id,
            "flowmon_or_kpi_present": archive_row is not None,
            "scenarios_rows": len(dataset_matches),
            "flowmon_access": expected_access,
            "scenarios_access": row.get("access_type", ""),
            "flowmon_cpe": expected_cpe,
            "scenarios_cpe": row.get("cpe", ""),
            "generated_source_default_mismatches": "|".join(source_default_by_run.get(run_id, [])),
            "top_level_scenario_metadata_mismatches": "|".join(top_level_by_run.get(run_id, [])),
            "issue_count": len(issues),
            "issues": "|".join(issues),
        })

    scenario_keys = [tuple(row["scenario_key"]) for row in run_records]
    duplicate_run_keys = {
        json.dumps(key): count
        for key, count in Counter(scenario_keys).items()
        if count > 1
    }
    all_scenario_ids = [row["scenario_id"] for row in dataset_rows]
    duplicate_scenario_ids = {
        key: count for key, count in Counter(all_scenario_ids).items() if count > 1
    }
    top_level_inconsistencies = Counter()
    with zipfile.ZipFile(ARCHIVE) as zf:
        for run_id in sorted(run_by_id):
            scenario = json.loads(xml_text(zf, run_id, "scenario.json"))
            expansion = scenario["expansion_parameters"]
            base_rate = scenario["traffic"]["data_rate"]
            base_speed = scenario["mobility"]["speed_mps"]
            base_lifi_rate = scenario["lifi"]["data_rate"]
            if base_rate != f"{float(expansion['offered_load_mbps']):g}Mbps":
                top_level_inconsistencies["scenario.traffic.data_rate_vs_expansion"] += 1
            if not nearly_equal(base_speed, expansion["mobility_speed_mps"]):
                top_level_inconsistencies["scenario.mobility.speed_mps_vs_expansion"] += 1
            if base_lifi_rate != f"{float(expansion['lifi_rate_mbps']):g}Mbps":
                top_level_inconsistencies["scenario.lifi.data_rate_vs_expansion"] += 1

    summary = {
        "expected": {
            "run_configurations": 48,
            "raw_flow_rows": 624,
            "application_flow_rows": 432,
            "application_flow_ids": list(APPLICATION_FLOW_IDS),
        },
        "observed": {
            "archive_run_configurations": len(run_records),
            "dataset_rows": len(dataset_rows),
            "dataset_run_ids": len({
                row["scenario_id"].rsplit("-flow-", 1)[0]
                for row in dataset_rows
                if "-flow-" in row["scenario_id"]
            }),
            "archive_application_keys": len({
                (row["run_id"], row["flow_id"])
                for row in recomputed_rows
                if row["is_application"]
            }),
        },
        "missing_configurations": sorted(set(run_by_id) - {
            row["scenario_id"].rsplit("-flow-", 1)[0]
            for row in dataset_rows if "-flow-" in row["scenario_id"]
        }),
        "extra_configurations": sorted({
            row["scenario_id"].rsplit("-flow-", 1)[0]
            for row in dataset_rows if "-flow-" in row["scenario_id"]
        } - set(run_by_id)),
        "duplicate_run_keys": duplicate_run_keys,
        "duplicate_application_flow_keys": duplicate_scenario_ids,
        "issue_counts": dict(issue_counts),
        "top_level_scenario_inconsistencies": dict(top_level_inconsistencies),
        "generated_source_default_inconsistencies": dict(Counter(
            mismatch
            for mismatches in source_default_by_run.values()
            for mismatch in mismatches
        )),
        "detail_rows_with_any_issue": sum(row["issue_count"] > 0 for row in detail_rows),
        "detail_rows": len(detail_rows),
    }
    return detail_rows, summary


def mean_sd(values: list[float]) -> tuple[float | None, float | None]:
    values = [float(v) for v in values if finite(float(v))]
    if not values:
        return None, None
    return statistics.fmean(values), (statistics.stdev(values) if len(values) > 1 else 0.0)


def grouped_sanity() -> tuple[list[dict[str, Any]], str, dict[str, Any]]:
    rows = load_dataset_rows()
    groups: dict[tuple[str, float, float, float], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        key = (
            row["access_type"],
            number(row["offered_load_mbps"]),
            number(row["mobility_speed_mps"]),
            number(row["lifi_rate_mbps"]),
        )
        groups[key].append(row)
    grouped: list[dict[str, Any]] = []
    for key, values in sorted(groups.items()):
        access, load, speed, lifi_rate = key
        output: dict[str, Any] = {
            "access_type": access,
            "offered_load_mbps": load,
            "mobility_speed_mps": speed,
            "lifi_rate_mbps": lifi_rate,
            "n_rows": len(values),
            "n_seeds": len({integer(row["random_seed"]) for row in values}),
            "n_cpes": len({row["cpe"] for row in values}),
        }
        for metric in ("throughput_mbps", "packet_loss_ratio", "mean_delay_ms", "mean_jitter_ms"):
            mean, sd = mean_sd([number(row[metric]) for row in values])
            output[f"{metric}_mean"] = mean
            output[f"{metric}_std"] = sd
        for metric in ("tx_packets", "rx_packets", "lost_packets"):
            mean, sd = mean_sd([number(row[metric]) for row in values])
            output[f"{metric}_mean"] = mean
            output[f"{metric}_std"] = sd
        output["access_diversity_values"] = sorted({
            number(row["access_diversity_score"]) for row in values
        })
        output["congestion_risk_counts"] = dict(Counter(row["congestion_risk"] for row in values))
        grouped.append(output)

    access_counts = Counter(row["access_type"] for row in rows)
    diversity_counts = Counter(row["access_diversity_score"] for row in rows)
    congestion_counts = Counter(row["congestion_risk"] for row in rows)
    surprises: list[str] = []

    if len(diversity_counts) == 1:
        surprises.append(
            "access_diversity_score is invariant in scenarios.csv: "
            f"{next(iter(diversity_counts))} across {sum(diversity_counts.values())} rows."
        )
    if all(number(row["packet_loss_ratio"]) == 0.0 for row in rows):
        surprises.append(
            "packet_loss_ratio is zero in all uploaded application rows; "
            "FlowMonitor tail-accounting gaps are reported separately."
        )
    if all(row["congestion_risk"] == "low" for row in rows):
        surprises.append("All uploaded rows are labelled low congestion risk.")
    if all(number(row["mean_jitter_ms"]) < 1e-3 for row in rows if row["access_type"] == "LiFi-surrogate"):
        surprises.append(
            "LiFi-surrogate jitter is below 1 microsecond in every uploaded LiFi row; "
            "this is consistent with the idealized CSMA/10 ns surrogate and is not a physical LiFi law."
        )

    # Compare paired parameter means without claiming monotonicity.
    effects: list[dict[str, Any]] = []
    for access in sorted(access_counts):
        for load in sorted({number(row["offered_load_mbps"]) for row in rows}):
            for metric in ("throughput_mbps", "packet_loss_ratio", "mean_delay_ms", "mean_jitter_ms"):
                low_mob = [
                    number(row[metric]) for row in rows
                    if row["access_type"] == access
                    and number(row["offered_load_mbps"]) == load
                    and number(row["mobility_speed_mps"]) == 0.5
                ]
                high_mob = [
                    number(row[metric]) for row in rows
                    if row["access_type"] == access
                    and number(row["offered_load_mbps"]) == load
                    and number(row["mobility_speed_mps"]) == 3.0
                ]
                low_mean, low_sd = mean_sd(low_mob)
                high_mean, high_sd = mean_sd(high_mob)
                effects.append({
                    "comparison": "mobility_3.0_minus_0.5",
                    "access_type": access,
                    "offered_load_mbps": load,
                    "metric": metric,
                    "low_mean": low_mean,
                    "high_mean": high_mean,
                    "difference": (high_mean - low_mean) if low_mean is not None and high_mean is not None else None,
                    "low_std": low_sd,
                    "high_std": high_sd,
                })
    for access in sorted(access_counts):
        for load in sorted({number(row["offered_load_mbps"]) for row in rows}):
            for speed in sorted({number(row["mobility_speed_mps"]) for row in rows}):
                for metric in ("throughput_mbps", "packet_loss_ratio", "mean_delay_ms", "mean_jitter_ms"):
                    low_rate = [
                        number(row[metric]) for row in rows
                        if row["access_type"] == access
                        and number(row["offered_load_mbps"]) == load
                        and number(row["mobility_speed_mps"]) == speed
                        and number(row["lifi_rate_mbps"]) == 50.0
                    ]
                    high_rate = [
                        number(row[metric]) for row in rows
                        if row["access_type"] == access
                        and number(row["offered_load_mbps"]) == load
                        and number(row["mobility_speed_mps"]) == speed
                        and number(row["lifi_rate_mbps"]) == 100.0
                    ]
                    low_mean, _ = mean_sd(low_rate)
                    high_mean, _ = mean_sd(high_rate)
                    effects.append({
                        "comparison": "lifi_rate_100_minus_50",
                        "access_type": access,
                        "offered_load_mbps": load,
                        "mobility_speed_mps": speed,
                        "metric": metric,
                        "low_mean": low_mean,
                        "high_mean": high_mean,
                        "difference": (high_mean - low_mean) if low_mean is not None and high_mean is not None else None,
                    })

    lines = [
        "# Sweep sanity report",
        "",
        "This report uses the existing 432 application-flow rows in "
        f"{SCENARIOS_CSV}. It is an empirical sanity analysis, not a proof of "
        "universal technology behaviour.",
        "",
        "## Coverage",
        "",
        f"- application rows: {len(rows)}",
        f"- access counts: {dict(access_counts)}",
        f"- offered loads: {sorted({number(row['offered_load_mbps']) for row in rows})}",
        f"- mobility speeds: {sorted({number(row['mobility_speed_mps']) for row in rows})}",
        f"- LiFi rates: {sorted({number(row['lifi_rate_mbps']) for row in rows})}",
        f"- seeds: {sorted({integer(row['random_seed']) for row in rows})}",
        "",
        "## Invariant or surprising behavior",
        "",
    ]
    lines.extend(f"- {item}" for item in surprises)
    lines.extend([
        "",
        "## Interpretation boundary",
        "",
        "- The low-load rows are approximately load-limited at the application-flow level.",
        "- High offered load should be described through the observed grouped means; no strict monotonicity is assumed.",
        "- Mobility differences are empirical deltas of this finite configuration, not a general mobility law.",
        "- LiFi-rate changes are relevant to the CSMA surrogate branch configuration; they do not validate a physical optical LiFi channel.",
        "- The uploaded packet_loss_ratio uses FlowMonitor lostPackets and is nonzero in some high-load Wi-Fi/LiFi-surrogate rows; it must not be presented as the complete terminal tx-rx loss because tx-rx gaps remain in every application flow.",
        "- access_diversity_score is a fixed postprocessing constant in the uploaded dataset, so it cannot support an independent access-diversity effect analysis.",
        "",
        "## Parameter contrasts",
        "",
        "The complete paired contrasts are available in grouped_kpi_summary.csv and "
        "in the JSON summary. They are reported as differences, not as universal rankings.",
        "",
        "## Evidence location",
        "",
        f"- grouped results: {OUT / 'grouped_kpi_summary.csv'}",
        f"- source table: {SCENARIOS_CSV}",
        "- semantic postprocessing implementation: /home/ubuntu/Desktop/LLM Driven wireless environment generation/src/llm_ns3/data_upload.py:364-405",
    ])
    summary = {
        "application_rows": len(rows),
        "access_counts": dict(access_counts),
        "access_diversity_counts": dict(diversity_counts),
        "congestion_risk_counts": dict(congestion_counts),
        "surprises": surprises,
        "effects": effects,
    }
    return grouped, "\n".join(lines) + "\n", summary


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
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(clean_json(row) for row in rows)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    recomputed, comparisons, archive_summary = archive_audit()
    consistency_rows, consistency_summary = consistency_audit(recomputed, archive_summary)
    grouped, sanity_report, sanity_summary = grouped_sanity()

    write_csv(OUT / "flowmonitor_recomputed.csv", recomputed)
    write_csv(OUT / "kpi_recomputation_comparison.csv", comparisons)
    write_csv(OUT / "sweep_consistency.csv", consistency_rows)
    write_csv(OUT / "grouped_kpi_summary.csv", grouped)
    write_json(OUT / "kpi_recomputation_summary.json", archive_summary)
    write_json(OUT / "sweep_consistency_summary.json", consistency_summary)
    write_json(OUT / "sweep_sanity_summary.json", sanity_summary)
    (OUT / "sweep_sanity_report.md").write_text(sanity_report, encoding="utf-8")

    print(json.dumps({
        "runs": archive_summary["run_count"],
        "recomputed_rows": archive_summary["raw_flow_rows"],
        "application_rows": archive_summary["application_flow_rows"],
        "consistency_issue_rows": consistency_summary["detail_rows_with_any_issue"],
        "accounting": archive_summary["packet_accounting"],
        "output": str(OUT),
    }, indent=2))


if __name__ == "__main__":
    CURRENT_SIM_TIME = 10.0
    main()
