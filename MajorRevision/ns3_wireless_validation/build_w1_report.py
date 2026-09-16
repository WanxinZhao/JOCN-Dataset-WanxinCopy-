#!/usr/bin/env python3
"""Render the W1 ns-3 evidence reports from the generated audit artifacts."""

from __future__ import annotations

import csv
import json
import math
import statistics
import zipfile
from collections import Counter, defaultdict
from pathlib import Path


WORKSPACE = Path("/home/ubuntu/Desktop/LLM Driven wireless environment generation")
PROJECT = WORKSPACE / "LLM-Driven-Multi-Agent-Optical-Digital-Twin-for-Automated-Data-Generation"
SWEEP = PROJECT / "NS3_Wireless_Hybrid_ParamSweep"
OUT = WORKSPACE / "W1_NS3_VALIDATION"
ARCHIVE = SWEEP / "artifacts.zip"
SCENARIOS = SWEEP / "scenarios.csv"
NS3_ROOT = Path("/home/ubuntu/Desktop/ns-allinone-3.44/ns-3.44")
NS3_BUILD = NS3_ROOT / "build"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def f(value: object, digits: int = 6) -> str:
    if value is None:
        return "MISSING"
    try:
        x = float(value)
    except (TypeError, ValueError):
        return str(value)
    if not math.isfinite(x):
        return "MISSING"
    return f"{x:.{digits}g}"


def mean(values: list[float]) -> float:
    return statistics.fmean(values) if values else float("nan")


def sd(values: list[float]) -> float:
    return statistics.stdev(values) if len(values) > 1 else 0.0


def table(rows: list[list[object]], headers: list[str]) -> str:
    output = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    output.extend("| " + " | ".join(str(cell) for cell in row) + " |" for row in rows)
    return "\n".join(output)


def zip_metadata() -> dict[str, object]:
    with zipfile.ZipFile(ARCHIVE) as zf:
        infos = zf.infolist()
        roots = sorted({info.filename.split("/", 1)[0] for info in infos if info.filename.endswith("/scenario.json")})
        source_hashes = Counter()
        for root in roots:
            import hashlib
            source_hashes[hashlib.sha256(zf.read(root + "/generated.cc")).hexdigest()] += 1
    return {
        "members": len(infos),
        "uncompressed": sum(info.file_size for info in infos),
        "compressed": sum(info.compress_size for info in infos),
        "roots": len(roots),
        "source_hashes": dict(source_hashes),
    }


def hash_file(path: Path) -> str:
    import hashlib
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def grouped_tables() -> tuple[str, dict[tuple[str, float, float, float], dict[str, str]]]:
    rows = read_csv(OUT / "grouped_kpi_summary.csv")
    by_key = {
        (r["access_type"], float(r["offered_load_mbps"]), float(r["mobility_speed_mps"]), float(r["lifi_rate_mbps"])): r
        for r in rows
    }
    app_rows = read_csv(SCENARIOS)
    keys = sorted({(r["access_type"], float(r["offered_load_mbps"])) for r in app_rows})
    summary: dict[tuple[str, float], dict[str, float]] = {}
    for access, load in keys:
        selected = [r for r in app_rows if r["access_type"] == access and float(r["offered_load_mbps"]) == load]
        summary[(access, load)] = {
            metric: mean([float(r[field]) for r in selected])
            for metric, field in {
                "throughput": "throughput_mbps",
                "loss": "packet_loss_ratio",
                "delay": "mean_delay_ms",
                "jitter": "mean_jitter_ms",
            }.items()
        }
    rows_out = []
    for access in ("LTE/EPC", "Wi-Fi", "LiFi-surrogate"):
        for load in (2.0, 5.0, 10.0, 20.0):
            s = summary[(access, load)]
            rows_out.append([access, f"{load:g}", f(s["throughput"]), f(s["loss"]), f(s["delay"]), f(s["jitter"])])
    return table(rows_out, ["Access branch", "Offered load (Mbps)", "Throughput (Mbps)", "FlowMonitor loss ratio", "Delay (ms)", "Jitter (ms)"]), by_key


def label_reason_counts() -> tuple[Counter, Counter, Counter]:
    rows = read_csv(SCENARIOS)
    labels = Counter(r["congestion_risk"] for r in rows)
    high_reasons = Counter()
    medium_reasons = Counter()
    for row in rows:
        sf = json.loads(row["semantic_features_json"])
        q = float(sf["queueing_risk_score"])
        loss = float(sf["packet_loss_ratio"])
        eff = float(sf["throughput_efficiency"])
        if row["congestion_risk"] == "high":
            high_reasons["queueing_risk >= 0.6"] += q >= 0.6
            high_reasons["packet_loss_ratio >= 0.05"] += loss >= 0.05
        if row["congestion_risk"] == "medium":
            medium_reasons["queueing_risk >= 0.2"] += q >= 0.2
            medium_reasons["throughput_efficiency < 0.8"] += eff < 0.8
    return labels, high_reasons, medium_reasons


def render_replay_report() -> None:
    execution = read_json(OUT / "replay_execution_summary.json")
    rows = read_csv(OUT / "replay_results.csv")
    table_rows = []
    for label, info in sorted(execution["replays"].items()):
        selected = [r for r in rows if r["replay_label"] == label]
        table_rows.append([
            label,
            info["run_id"],
            info["compile_returncode"],
            info["run_returncode"],
            info["application_flow_count"],
            f(max(float(r["abs_delta_throughput_mbps"]) for r in selected)),
            f(max(float(r["abs_delta_packet_loss_ratio"]) for r in selected)),
            f(max(float(r["abs_delta_mean_delay_ms"]) for r in selected)),
            f(max(float(r["abs_delta_mean_jitter_ms"]) for r in selected)),
        ])
    lines = [
        "# Representative replay report",
        "",
        "Each replay compiled the exact archived `generated.cc` for the selected run with `/usr/bin/c++` and the existing ns-3.44 build libraries, then executed it with the archived parameter values. The simulator was run from the workspace with a relative output directory because the installed CommandLine path handling did not accept an absolute path containing spaces. The parameter values are unchanged.",
        "",
        table(table_rows, ["Replay", "Archive run", "Compile rc", "Run rc", "Application flows", "Max abs throughput delta", "Max abs loss delta", "Max abs delay delta", "Max abs jitter delta"]),
        "",
        "All three replays built and executed successfully and produced nine classifier-identified application flows. All listed numerical deltas are zero under the independent XML parser. The full per-flow values are in `replay_results.csv`; commands and logs are below each replay directory.",
        "",
        "## Commands",
        "",
        "```text",
        "W1_NS3_VALIDATION/replays/low_load_low_mobility/archived_generated_rebuilt --outputDir=W1_NS3_VALIDATION/replays/low_load_low_mobility/fresh_results --simTime=10.0 --seed=1 --offeredLoadMbps=2 --packetSize=1024 --mobilitySpeed=0.5 --lifiRateMbps=50",
        "W1_NS3_VALIDATION/replays/medium_load_high_mobility/archived_generated_rebuilt --outputDir=W1_NS3_VALIDATION/replays/medium_load_high_mobility/fresh_results --simTime=10.0 --seed=2 --offeredLoadMbps=10 --packetSize=1024 --mobilitySpeed=3 --lifiRateMbps=100",
        "W1_NS3_VALIDATION/replays/high_load_high_mobility/archived_generated_rebuilt --outputDir=W1_NS3_VALIDATION/replays/high_load_high_mobility/fresh_results --simTime=10.0 --seed=3 --offeredLoadMbps=20 --packetSize=1024 --mobilitySpeed=3 --lifiRateMbps=100",
        "```",
        "",
        "The exact compile command for each source is recorded in its `compile.log`; run stdout/stderr and command are recorded in its `run.log`.",
    ]
    (OUT / "replay_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def render_claim_boundary() -> None:
    lines = [
        "# ns-3 claim and terminology boundary",
        "",
        "This lock is based on the archived source and the W1 validation evidence. It is intended to prevent the synthetic wireless results from being described as physical measurements or as technology-universal laws.",
        "",
        "## Terminology that is supported",
        "",
        table([
            ["LTE/EPC", "Stock ns-3 LTE helper plus PointToPointEpcHelper; archived source `generated.cc:L141-L152`.", "Use `LTE/EPC`; do not call this 5G NR."],
            ["Wi-Fi 802.11n", "`wifi.SetStandard(WIFI_STANDARD_80211n)` with Yans channel/PHY; `generated.cc:L112-L124`.", "Use Wi-Fi 802.11n for this synthetic branch. A separate physical testbed can be described independently."],
            ["CSMA-based LiFi surrogate", "`CsmaHelper`, 50/100 Mbps and 10 ns delay; `generated.cc:L130-L139`.", "Call it an idealized CSMA-based LiFi surrogate."],
            ["Finite configuration-specific comparison", "48 archived configurations, grouped in `grouped_kpi_summary.csv`.", "Report observed deltas for this sweep only."],
        ], ["Supported label", "Evidence", "Claim form"]),
        "",
        "## Claims that are not supported",
        "",
        table([
            ["5G NR performance", "The implementation is LTE/EPC; `/home/ubuntu/Desktop/LLM Driven wireless environment generation/src/llm_ns3/schema.py:L125-L129` explicitly rejects 5G NR in this install.", "Unsupported."],
            ["Physical LiFi propagation", "No optical LOS/FOV geometry, photodiode, optical modulation, shot noise, blockage, or calibrated optical error model is present in the CSMA branch.", "Unsupported."],
            ["Universal ranking such as LiFi always has lower delay/jitter", "The lower jitter occurs under the idealized CSMA/10 ns configuration and changes at high load.", "Unsupported; phrase as an observed configuration-specific result."],
            ["Measured wireless testbed validation", "This artifact is synthetic ns-3 output; no measured wireless ground truth is part of this validation.", "Unsupported."],
            ["Zero terminal packet loss", "FlowMonitor `lostPackets` is not equal to `txPackets-rxPackets` at the exact 10 s stop.", "Unsupported unless a separate terminal-loss definition is reported."],
        ], ["Overclaim", "Reason", "Boundary"]),
        "",
        "Recommended sentence: `Under the adopted idealized CSMA-based LiFi-surrogate configuration, the surrogate branch exhibits the observed delay/jitter behaviour relative to the LTE/EPC and Wi-Fi branches; this is not a physical LiFi propagation result.`",
        "",
        "Evidence: `/home/ubuntu/Desktop/LLM Driven wireless environment generation/W1_NS3_VALIDATION/kpi_recomputation_summary.json`, `grouped_kpi_summary.csv`, `replay_results.csv`, and this file.",
    ]
    (OUT / "ns3_claim_boundary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def render_primary() -> None:
    kpi = read_json(OUT / "kpi_recomputation_summary.json")
    consistency = read_json(OUT / "sweep_consistency_summary.json")
    sanity = read_json(OUT / "sweep_sanity_summary.json")
    replay = read_json(OUT / "replay_execution_summary.json")
    reference = read_json(OUT / "independent_reference/summary.json")
    app_rows = read_csv(SCENARIOS)
    recomputed = read_csv(OUT / "flowmonitor_recomputed.csv")
    grouped, grouped_lookup = grouped_tables()
    labels, high_reasons, medium_reasons = label_reason_counts()
    zip_info = zip_metadata()
    archive_sha = hash_file(ARCHIVE)
    scenarios_sha = hash_file(SCENARIOS)
    app_recomputed = [row for row in recomputed if row["is_application"] == "True"]
    accounting = kpi["packet_accounting"]
    branch_accounting = {}
    for access in ("LTE/EPC", "Wi-Fi", "LiFi-surrogate"):
        selected = [row for row in app_recomputed if row["access_type"] == access]
        branch_accounting[access] = {
            "rows": len(selected),
            "tx_minus_rx": sum(int(row["tx_minus_rx"]) for row in selected),
            "flowmonitor_lost": sum(int(row["lost_packets"]) for row in selected),
            "accounting_gap": sum(int(row["accounting_gap"]) for row in selected),
        }

    app_metric_rows = []
    for metric in ("tx_packets", "rx_packets", "lost_packets", "throughput_mbps", "mean_delay_ms", "mean_jitter_ms"):
        item = kpi["metrics"][metric]["application_flow_rows"]
        app_metric_rows.append([
            metric,
            item["compared_records"],
            item["exact_numeric_matches"],
            item["within_tolerance_records"],
            f(item["maximum_absolute_error"]),
            f(item["mean_absolute_error"]),
            f(item["maximum_relative_error_nonzero_reference"]),
        ])
    all_metric_rows = []
    for metric in ("tx_packets", "rx_packets", "lost_packets", "throughput_mbps", "mean_delay_ms", "mean_jitter_ms"):
        item = kpi["metrics"][metric]["all_flow_rows"]
        all_metric_rows.append([
            metric,
            item["compared_records"],
            item["exact_numeric_matches"],
            item["within_tolerance_records"],
            f(item["maximum_absolute_error"]),
            f(item["mean_absolute_error"]),
            f(item["maximum_relative_error_nonzero_reference"]),
        ])

    replay_rows = []
    replay_csv = read_csv(OUT / "replay_results.csv")
    for label, info in sorted(replay["replays"].items()):
        selected = [r for r in replay_csv if r["replay_label"] == label]
        replay_rows.append([
            label,
            info["run_id"],
            info["compile_returncode"],
            info["run_returncode"],
            info["application_flow_count"],
            f(max(float(r["abs_delta_throughput_mbps"]) for r in selected)),
            f(max(float(r["abs_delta_packet_loss_ratio"]) for r in selected)),
            f(max(float(r["abs_delta_mean_delay_ms"]) for r in selected)),
            f(max(float(r["abs_delta_mean_jitter_ms"]) for r in selected)),
        ])

    repeat = read_json(OUT / "replay_execution_summary.json")["repeatability"]
    seed_rows = read_csv(OUT / "seed_sensitivity.csv")
    seed_table = []
    for row in seed_rows:
        if row["metric"] in {"throughput_mbps", "packet_loss_ratio", "mean_delay_ms", "mean_jitter_ms"}:
            seed_table.append([
                row["access_type"], row["metric"], row["n_application_flows"],
                f(row["all_flow_mean"]), f(row["all_flow_std"]),
                f(row["seed1_mean"]), f(row["seed2_mean"]), f(row["seed3_mean"]), f(row["seed_mean_std"]),
            ])

    metadata_table = table([
        ["Dataset", "NS3_Wireless_Hybrid_ParamSweep"],
        ["Source path", str(SWEEP)],
        ["Physical testbed", "None; synthetic ns-3.44 discrete-event scenario"],
        ["Simulation duration", "10 s per run"],
        ["Sampling interval", "N/A; packet-level event-driven simulation"],
        ["Run/configuration count", "48 (4 loads × 2 speeds × 2 LiFi rates × 3 seeds)"],
        ["Application records", "432 (9 application flows × 48 runs)"],
        ["Raw FlowMonitor rows", "624 (13 rows × 48 runs; 9 application + 4 infrastructure/control)"],
        ["Application features", "tx/rx/lost packets; throughput; mean delay; mean jitter; configuration fields"],
        ["Branches", "LTE/EPC; Wi-Fi 802.11n; CSMA-based LiFi surrogate"],
        ["Labels", "No external ground-truth labels; congestion_risk is deterministic postprocessing"],
        ["Archived output files", "48 generated.cc, 48 FlowMonitor XML, 48 kpi.csv, 48 build logs, 48 run logs, plus prompts/reviews/scenario/status JSON"],
        ["Files", "CSV, JSON, FlowMonitor XML, C++, logs, ZIP"],
        ["Archive size", f"{ARCHIVE.stat().st_size} bytes compressed; {zip_info['uncompressed']} bytes member payload"],
        ["Missing/nonfinite compact cells", "0 blank cells; 0 nonfinite relevant numeric cells"],
        ["Terms", "README says academic research/non-commercial use; no SPDX identifier located"],
    ], ["Field", "Observed value"])

    lines = [
        "# WIRELESS_REVISION_W1_NS3_VALIDATION",
        "",
        "W1 validation scope: only the archived synthetic wireless ns-3 dataset and its simulation evidence. Optical data, semantic-fusion experiments, manuscript text, commits, pushes, and large new simulations were not modified or run.",
        "",
        "## Evidence labels",
        "",
        "- **OBSERVED**: directly read from code, archive artifacts, output files, logs, or the W1 validation outputs.",
        "- **INFERRED**: interpretation derived from an observed implementation or result, without an explicit source statement.",
        "- **MISSING**: not recoverable from the inspected wireless artifacts.",
        "",
        "## 1. Executive verdict",
        "",
        "**PASS_WITH_LIMITATIONS**.",
        "",
        "**OBSERVED:** all 48 archived configurations are present and marked completed; the archive contains 624 raw FlowMonitor rows and 432 application-flow rows. An independent XML parser reconstructs all rows. Application packet counters and FlowMonitor lost-packet counts match the archived `kpi.csv` exactly; application throughput, delay, and jitter agree within XML serialization precision. All three representative archived sources were rebuilt with the available ns-3.44 libraries, executed, and produced nine application flows with zero numerical deltas against their archived FlowMonitor results. The medium configuration is deterministic under two same-seed repeats. A separate hand-written ns-3.44 reference produces the same nine classifier-keyed application flows and all 63 compared values.",
        "",
        "**LIMITATION:** FlowMonitor `lostPackets` is not terminal `txPackets-rxPackets` at the exact 10 s stop. The current `packet_loss_ratio` is therefore a FlowMonitor loss ratio, not a complete end-to-end terminal loss ratio. The expanded `scenario.json` retains base metadata values for traffic rate, mobility speed, and sometimes LiFi rate while the actual sweep values are carried in `expansion_parameters` and passed by CLI. These are claim/metadata limitations, not evidence of a corrupted simulation binary.",
        "",
        "**INFERRED:** the current 48-run dataset is usable for a bounded, configuration-specific feasibility result if the revision explicitly labels it synthetic, uses LTE/EPC and CSMA-based LiFi-surrogate terminology, reports the FlowMonitor loss definition, and does not infer physical LiFi or universal technology rankings.",
        "",
        "## 2. ns-3 execution environment",
        "",
        table([
            ["Version", "3.44", f"{NS3_ROOT / 'VERSION'}:1"],
            ["Source/build root", str(NS3_ROOT), str(NS3_BUILD)],
            ["Build profile", "default; Unix Makefiles; CMake `CMAKE_BUILD_TYPE=default`", f"{NS3_BUILD / 'CMakeCache.txt'}:30,714"],
            ["Compiler", "/usr/bin/c++ GNU 15.2.0 (Ubuntu 15.2.0-16ubuntu1)", "`/usr/bin/c++ --version`"],
            ["Validation compile flags", "C++20, -Os, -g, -DNDEBUG, ns-3 build includes, libxml2", f"{NS3_BUILD / 'scratch/CMakeFiles/scratch_llm_ns3_20260511T163516Z_indoor_hybrid.dir/flags.make'}:5-10"],
            ["Archive", str(ARCHIVE), f"SHA-256 {archive_sha}"],
            ["Archive source diversity", "one byte-identical generated.cc SHA-256 across all 48 roots", f"SHA-256 {next(iter(zip_info['source_hashes']))}"],
        ], ["Item", "Observed value", "Evidence"]),
        "",
        "The archived expansion wrapper uses the ns-3 launcher and passes the six scenario parameters at `/home/ubuntu/Desktop/LLM Driven wireless environment generation/src/llm_ns3/data_expand.py:_run_ns3_variant`, lines 150-205, especially lines 184-190. For W1, the exact archived sources were copied to `W1_NS3_VALIDATION/replays/`, compiled directly with `/usr/bin/c++`, and executed against the existing build libraries. This avoids rebuilding Python bindings and does not modify the ns-3 source/build tree. The exact commands are in `W1_NS3_VALIDATION/replays/*/compile.log` and `run.log`.",
        "",
        "## 3. Full 48-run FlowMonitor KPI recomputation",
        "",
        "**OBSERVED:** `W1_NS3_VALIDATION/archive_audit.py:parse_flowmon` parses FlowMonitor XML independently of `/home/ubuntu/Desktop/LLM Driven wireless environment generation/src/llm_ns3/data_upload.py`. The parser derives the application mapping from XML classifier addresses and UDP destination port 9, then applies the KPI equations used by the archived generated source at `W1_NS3_VALIDATION/replays/medium_load_high_mobility/archived_generated.cc:L215-L222`:",
        "",
        "- `duration = timeLastRxPacket - timeFirstTxPacket`; if non-positive, use `simTime - 1` for a 10 s run.",
        "- `throughput_mbps = rxBytes * 8 / duration / 1e6`.",
        "- `mean_delay_ms = delaySum_seconds * 1000 / rxPackets` when `rxPackets > 0`.",
        "- `mean_jitter_ms = jitterSum_seconds * 1000 / (rxPackets - 1)` when `rxPackets > 1`.",
        "",
        table(app_metric_rows, ["Metric", "Compared application rows", "Exact matches", "Within audit tolerance", "Max absolute error", "Mean absolute error", "Max relative error"]),
        "",
        "For completeness, the same independent comparison over all 624 rows (including four infrastructure/control flows per run) is:",
        "",
        table(all_metric_rows, ["Metric", "Compared all rows", "Exact matches", "Within audit tolerance", "Max absolute error", "Mean absolute error", "Max relative error"]),
        "",
        "The application audit tolerances are 1e-6 for packet counters and 1e-4 in the reported metric units for continuous metrics. The maximum application differences are 5.57e-5 Mbps throughput, 3.16e-3 ms delay, and 1.10e-5 ms jitter; their relative errors are at most approximately 6.32e-6. The larger all-flow throughput discrepancy (maximum 2555 Mbps) occurs only in short infrastructure/control flows whose XML times are rounded at a scale comparable to their sub-microsecond duration; those four flow IDs are not exported as application rows. The all-flow comparison is retained in `kpi_recomputation_summary.json` rather than hidden.",
        "",
        "**OBSERVED physical checks:** zero negative recomputed values, zero nonfinite recomputed values, and zero archived FlowMonitor loss ratios outside [0,1]. The evidence files are `flowmonitor_recomputed.csv`, `kpi_recomputation_comparison.csv`, and `kpi_recomputation_summary.json`.",
        "",
        "### Packet accounting",
        "",
        table([
            [access, data["rows"], data["tx_minus_rx"], data["flowmonitor_lost"], data["accounting_gap"]]
            for access, data in branch_accounting.items()
        ], ["Branch", "Application rows", "Σ(tx-rx)", "Σ FlowMonitor lostPackets", "Σ(tx-rx-lostPackets)"]),
        "",
        f"**OBSERVED:** `tx_packets-rx_packets` is nonzero in {accounting['tx_minus_rx_nonzero']}/{accounting['application_flows']} application flows, while FlowMonitor `lostPackets` is nonzero in {accounting['flowmonitor_lost_nonzero']}/{accounting['application_flows']}. The relation `lost_packets == tx_packets-rx_packets` therefore does not hold for the archived application flows.",
        "",
        f"**OBSERVED explanation from the installed ns-3 source:** `FlowMonitor::MaxPerHopDelay` defaults to 10 s at `/home/ubuntu/Desktop/ns-allinone-3.44/ns-3.44/src/flow-monitor/model/flow-monitor.cc:L36-L42`; `CheckForLostPackets(Time)` increments `lostPackets` only for still-tracked packets whose age reaches that delay at `L320-L341`; explicit probe drops also increment it at `L274-L310`. The generated program stops at exactly 10 s (`archived_generated.cc:L203`) and serializes at that time (`flow-monitor.cc:L431-L453`). Thus packets still in flight or not yet beyond the timeout can contribute to `tx-rx` without appearing in `lostPackets`.",
        "",
        "**Claim boundary:** the archived field is correctly extracted as the FlowMonitor-reported loss count, but the column name/interpretation must be qualified as `FlowMonitor loss ratio`; it is not evidence of zero terminal packet loss.",
        "",
        "## 4. End-to-end sweep consistency",
        "",
        "**OBSERVED:** the archive has 48 unique full scenario keys and each root has 13 FlowMonitor rows, nine XML-classifier-identified application rows, and 13 `kpi.csv` rows. `sweep_consistency.csv` contains 432 expected application keys; all 432 are present exactly once in `scenarios.csv`; no missing/extra configurations, duplicate full run keys, duplicate application keys, flow ID mismatches, access mapping mismatches, CPE mismatches, or KPI mismatches were found.",
        "",
        table([
            ["Expected run configurations", 48, consistency["observed"]["archive_run_configurations"]],
            ["Expected raw FlowMonitor/KPI rows", 624, kpi["raw_flow_rows"]],
            ["Expected application rows", 432, consistency["observed"]["dataset_rows"]],
            ["Application FlowMonitor IDs", "5-13", "5-13 in every root"],
            ["Structural issue rows", 0, consistency["detail_rows_with_any_issue"]],
            ["Archive status", "completed", "48/48 status.json files"],
        ], ["Check", "Expected", "Observed"]),
        "",
        "The independent XML classifier mapping is: IDs 5-7 LTE/EPC CPE1-CPE3, IDs 8-10 Wi-Fi CPE1-CPE3, and IDs 11-13 LiFi-surrogate CPE1-CPE3. This agrees with the export mapping in `/home/ubuntu/Desktop/LLM Driven wireless environment generation/src/llm_ns3/data_upload.py:_flow_access_map`, lines 255-273, but W1 did not use that function as its primary mapping source.",
        "",
        "### Parameter provenance nuance",
        "",
        "**OBSERVED:** `/home/ubuntu/Desktop/LLM Driven wireless environment generation/src/llm_ns3/data_expand.py:_create_variant_run`, lines 131-146, writes the sweep values to `scenario.expansion_parameters`; `_run_ns3_variant`, lines 184-190, passes them on the command line. `/home/ubuntu/Desktop/LLM Driven wireless environment generation/src/llm_ns3/data_upload.py:_ns3_config`, lines 299-320, records those CLI values in `ns3_config_json`. The actual 48 status records and 432 exported rows therefore carry the intended expansion values.",
        "",
        "**OBSERVED limitation:** the base scenario fields were not rewritten for every expanded variant. Across the 48 roots: `scenario.traffic.data_rate` disagrees with expansion in 36, `scenario.mobility.speed_mps` in 48, and `scenario.lifi.data_rate` in 24. All 48 archived sources retain the same defaults (`simTime=10`, `seed=1`, `offeredLoadMbps=10`, `packetSize=1024`, `mobilitySpeed=1.5`, `lifiRateMbps=100`); source-default mismatches against the intended CLI parameters are seed 32, offered load 36, mobility 48, LiFi rate 24, with no mismatch for duration or packet size. Running a source without the recorded CLI overrides would not reproduce its expanded scenario. W1 replays used the recorded CLI parameters.",
        "",
        "This is a reproducibility/metadata issue to correct in the released manifest or export logic; it did not create a structural mismatch in the archived executed outputs because the actual commands are recorded in `ns3_config_json` and `status.json`.",
        "",
        "## 5. Scientific sweep sanity analysis",
        "",
        "The grouped file has 48 groups (three branches × four loads × two mobility speeds × two LiFi rates), nine application rows per group, three seeds, and three CPEs. The following table averages equally over the relevant seeds, CPEs, mobility values, and LiFi rates; it is descriptive, not a universal technology ranking.",
        "",
        grouped,
        "",
        "**OBSERVED:** low-load application throughput is approximately offered-load limited. At 10 and 20 Mbps, LTE/EPC saturates near 5.83 Mbps in this configuration, while Wi-Fi and the LiFi surrogate show high-load delay/loss changes. The exact 48-group values, standard deviations, seed counts, and CPE counts are in `grouped_kpi_summary.csv`.",
        "",
        "**OBSERVED parameter contrasts:** LiFi-rate changes are exactly invariant for LTE/EPC and Wi-Fi in the grouped results, as expected from branch separation. For the LiFi surrogate, the 50-to-100 Mbps difference is negligible at 2-10 Mbps but at 20 Mbps is approximately +4.339 Mbps throughput, -677.266 ms delay, and -0.240 ms jitter. Mobility changes are exactly invariant for LTE/EPC and LiFi-surrogate in the grouped output; for Wi-Fi the high-load 3.0-minus-0.5 m/s contrast is approximately -0.592 Mbps throughput and +81.15 ms delay. These are empirical properties of this finite model, not physical laws.",
        "",
        "**OBSERVED postprocessing behaviour:** `access_diversity_score` is exactly 0.75 for all 432 rows because `/home/ubuntu/Desktop/LLM Driven wireless environment generation/src/llm_ns3/data_upload.py:_semantic_features`, lines 380-383, assigns a constant per branch. It cannot support a simulated access-diversity effect. `congestion_risk` counts are low 306, medium 84, high 42. The code at lines 376-390 uses fixed thresholds rather than a learned label model: high is `queueing_risk_score >= 0.6` or `packet_loss_ratio >= 0.05`; medium is `queueing_risk_score >= 0.2` or throughput efficiency `< 0.8`; otherwise low. All 42 high rows meet both high conditions; 72 medium rows are triggered by efficiency and 12 by queueing risk. Labels are therefore deterministic thresholded postprocessing, not independent ground truth.",
        "",
        "**OBSERVED/inferred realism boundary:** LiFi-surrogate jitter is sub-microsecond in much of the low/medium-load output but rises at high load. The observed low jitter is consistent with the CSMA/10 ns surrogate; it should not be interpreted as a physical optical LiFi result. The Yans Wi-Fi branch and stock LTE/EPC branch have no custom calibrated cross-technology error model in the archived source, so cross-branch differences are configuration-specific.",
        "",
        "## 6. Representative replay results",
        "",
        table(replay_rows, ["Configuration", "Archive run", "Compile rc", "Run rc", "App flows", "Max abs throughput delta", "Max abs loss delta", "Max abs delay delta", "Max abs jitter delta"]),
        "",
        "**OBSERVED:** low-load/low-mobility (2 Mbps, 0.5 m/s, 50 Mbps, seed 1), medium (10 Mbps, 3 m/s, 100 Mbps, seed 2), and high-load/high-mobility (20 Mbps, 3 m/s, 100 Mbps, seed 3) were all rebuilt and executed. Each produced nine application flows. All packet counters and all four independently parsed KPI deltas are zero. This is stronger than a build-only check, but it is still a three-configuration replay rather than a fresh rerun of all 48 configurations.",
        "",
        "Evidence: `W1_NS3_VALIDATION/replay_results.csv`, `replay_report.md`, and `replays/{low_load_low_mobility,medium_load_high_mobility,high_load_high_mobility}/`.",
        "",
        "## 7. Same-seed repeatability",
        "",
        f"The medium configuration `{repeat['run_id']}` was executed twice with the same rebuilt source, ns-3.44 libraries, seed 2, parameters, and command structure. **OBSERVED:** both runs returned 0, both produced nine application flows, all four KPI exact-match counts are 9/9, and maximum absolute differences are throughput {f(repeat['max_abs_deltas']['throughput_mbps'])}, loss {f(repeat['max_abs_deltas']['packet_loss_ratio'])}, delay {f(repeat['max_abs_deltas']['mean_delay_ms'])}, and jitter {f(repeat['max_abs_deltas']['mean_jitter_ms'])}. The implementation is deterministic for this fixed build and configuration.",
        "",
        "This does not establish bitwise reproducibility across a different compiler, ns-3 build, operating system, or unrecorded run number. The generated source calls `RngSeedManager::SetSeed(seed)` at `archived_generated.cc:L37` and does not call `RngSeedManager::SetRun`; the archive uses seeds 1, 2, and 3 as separate configurations.",
        "",
        "## 8. Three-seed sensitivity",
        "",
        "The fixed configuration is offered load 10 Mbps, mobility 3 m/s, LiFi-surrogate rate 100 Mbps, packet size 1024, and duration 10 s. Values below use the FlowMonitor loss definition and aggregate the nine application flows (three CPEs × seeds 1-3). `all-flow mean ± SD` is across those nine flow values; seed columns are per-seed CPE means and `seed-mean SD` is the SD across the three seed means.",
        "",
        table(seed_table, ["Access", "Metric", "n", "All-flow mean", "All-flow SD", "Seed 1", "Seed 2", "Seed 3", "Seed-mean SD"]),
        "",
        "**OBSERVED:** seed sensitivity is very small for LTE/EPC and the LiFi surrogate at this fixed point, while Wi-Fi shows larger seed variation (throughput seed means approximately 10.264, 10.266, and 9.888 Mbps). This is why the revision should retain mean/SD or confidence intervals and avoid presenting one run as a universal branch ranking.",
        "",
        "Evidence: `W1_NS3_VALIDATION/repeatability.csv` and `seed_sensitivity.csv`.",
        "",
        "## 9. Independent hand-written ns-3 baseline",
        "",
        "**OBSERVED:** `W1_NS3_VALIDATION/independent_reference/reference.cc` is a new fixed-configuration C++ program, written separately from the archived generated source. It manually instantiates three CPEs, Wi-Fi 802.11n, LTE/EPC, the CSMA-based LiFi surrogate, the same 10 Mbps/1024-byte/10 s/3 m/s/100 Mbps/seed-2 operating point, and nine downlink UDP flows. It uses FlowMonitor and emits its own XML and manifest.",
        "",
        table([
            [metric, detail["records"], detail["consistent"], detail["materially_different"], f(detail["max_absolute_delta"])]
            for metric, detail in reference["metric_counts"].items()
        ], ["Metric", "Records", "CONSISTENT", "MATERIALLY_DIFFERENT", "Max absolute delta"]),
        "",
        f"**OBSERVED:** generated and reference XML each have {reference['generated_flow_count']} application flows; all expected flows are present. All {sum(d['records'] for d in reference['metric_counts'].values())} keyed metric comparisons are CONSISTENT, including exact equality for packet counters and FlowMonitor loss, and zero numerical delta for throughput, delay, and jitter. The independent topology/configuration checks are {reference['topology']['consistent']}/{reference['topology']['checks']} CONSISTENT (flow count, access/CPE keys, destination addresses/ports, three CPEs per branch, and mapping correspondence). The comparison key is XML classifier-derived access branch and CPE rather than numeric flow ID. Continuous KPI tolerance is max(1e-6, 1% of the generated value); counter/loss tolerance is exact.",
        "",
        "**INFERRED:** this independently validates the declared topology/access mapping and the archived KPI behaviour under the same stock ns-3.44 assumptions. It does not validate physical realism, LiFi optical physics, or the LLM’s historical generation quality.",
        "",
        "Evidence: `W1_NS3_VALIDATION/independent_reference/reference.cc`, `comparison.csv`, `topology_config_comparison.csv`, `report.md`, `compile.log`, `run.log`.",
        "",
        "## 10. Model and terminology lock",
        "",
        "The source-level evidence is:",
        "",
        "- **LTE/EPC:** `LteHelper` + `PointToPointEpcHelper` at archived source lines 141-152. The schema explicitly states that 5G NR is unsupported at `/home/ubuntu/Desktop/LLM Driven wireless environment generation/src/llm_ns3/schema.py:125-129`.",
        "- **Wi-Fi 802.11n:** `WIFI_STANDARD_80211n`, `YansWifiChannelHelper::Default`, and `YansWifiPhyHelper` at lines 112-124. The scenario metadata says 20 MHz, but the generated source does not explicitly set a channel-width attribute; the revision should not present 20 MHz as independently validated by the source unless this is clarified.",
        "- **CSMA-based LiFi surrogate:** `CsmaHelper`, swept 50/100 Mbps, and 10 ns delay at lines 130-139. No optical LOS/FOV, photodiode, optical modulation, shot-noise, blockage, or calibrated optical error model is present in this branch.",
        "",
        "The locked wording and unsupported claims are in `W1_NS3_VALIDATION/ns3_claim_boundary.md`.",
        "",
        "## 11. Reviewer-ready evidence",
        "",
        table([
            ["R3-4: generated data lack independent correctness validation", "Independent FlowMonitor XML recomputation for all 48; three source replays; same-seed repeat; hand-written reference", "`kpi_recomputation_summary.json`, `replay_results.csv`, `repeatability.csv`, `independent_reference/comparison.csv`", "Archive counters/mapping pass; three replays exact; 63 reference comparisons consistent", "The archived synthetic KPI extraction and declared representative configurations are reproducible and independently checked", "No physical ground truth; terminal loss differs from FlowMonitor lostPackets at the 10 s cutoff"],
            ["R3-3: LLM framework insufficiently evaluated (wireless correctness aspect)", "Rebuild archived generated source and compare against a separate stock-API reference", "`replays/*/compile.log`, `independent_reference/reference.cc` and report", "Representative source executes and agrees with independent declared configuration", "The wireless simulation output is not accepted solely because code compiled; it passed structural/numerical checks", "This does not provide missing token/cost/history logs or evaluate the full LLM framework"],
            ["R3-10: ns-3 terminology", "Source and output model audit", "`ns3_claim_boundary.md`; archived source lines 112-152", "Terminology locked to LTE/EPC, Wi-Fi 802.11n, CSMA LiFi surrogate", "Use configuration-specific synthetic claims", "No 5G NR or physical LiFi claim is supported"],
            ["R1: dataset summary", "Synthetic dataset metadata extraction", "`summary.json`, `scenarios.csv`, `artifacts.zip`, metadata table below", "48 runs, 432 app rows, 624 raw rows, parameter coverage and file terms recorded", "Add a separate synthetic-wireless dataset row/table", "README provides non-commercial academic terms but no SPDX identifier"],
        ], ["Reviewer concern", "Experiment performed", "Evidence", "Result", "Claim now supported", "Remaining limitation"]),
        "",
        "### Reviewer 1 metadata material",
        "",
        metadata_table,
        "",
        f"The wireless synthetic table is separate from any real wireless measurement campaign. `scenarios.csv` has 58 columns and SHA-256 {scenarios_sha}; `artifacts.zip` has {zip_info['members']} members ({zip_info['uncompressed']} uncompressed payload bytes). The repository README states academic research/non-commercial use at `/home/ubuntu/Desktop/LLM Driven wireless environment generation/LLM-Driven-Multi-Agent-Optical-Digital-Twin-for-Automated-Data-Generation/README.md:118-119`; no formal SPDX identifier was found in the inspected wireless project materials.",
        "",
        "## 12. Exact recommendation for manuscript revision",
        "",
        "1. Add the W1 independent correctness evidence as a reproducibility subsection or supplementary table: archive-wide XML recomputation, three representative replays, same-seed repeatability, and the hand-written stock-ns-3 reference.",
        "2. Replace generic or universal wireless ranking statements with the bounded wording in `ns3_claim_boundary.md`. Use LTE/EPC, Wi-Fi 802.11n, and CSMA-based LiFi surrogate consistently.",
        "3. State that the 48-run wireless artifact is synthetic, packet-level ns-3.44 output with 3 CPEs, 9 application flows per run, 10 s duration, loads 2/5/10/20 Mbps, speeds 0.5/3 m/s, LiFi-surrogate rates 50/100 Mbps, and seeds 1/2/3.",
        "4. Rename or explicitly qualify `packet_loss_ratio` as FlowMonitor loss ratio, and state that `tx-rx` terminal accounting is not identical at the exact simulation stop. If the paper requires terminal end-to-end loss, a separate grace-period rerun/re-export is needed; W1 did not alter the archived data.",
        "5. Correct the released metadata so the expanded parameters are the canonical scenario fields, or make the recorded CLI command the formal source of truth. Do not run an expanded source with its stale defaults and call it the corresponding variant.",
        "6. Keep the physical LiFi limitation explicit: the current branch has no optical geometry or calibrated optical channel. Report its low-jitter/high-throughput behaviour only as an observed property of the idealized CSMA surrogate.",
        "",
        "### Regeneration decision",
        "",
        "**DATASET_REGENERATION_REQUIRED:** not required to establish current FlowMonitor extraction, structural mapping, representative replay, or same-build repeatability. It is conditionally required only if the manuscript intends to claim terminal packet loss rather than FlowMonitor loss, or if authors choose to eliminate the stale base-field metadata instead of documenting/repairing the export manifest. No old result was silently patched.",
        "",
        "## Final status",
        "",
        "W1_NS3_VERDICT=PASS_WITH_LIMITATIONS",
        "FLOWMONITOR_RECOMPUTATION=PASS_APPLICATION_ROWS_WITH_XML_SERIALIZATION_LIMITATION_AND_EXPLICIT_LOSS_ACCOUNTING_GAP",
        "SWEEP_CONSISTENCY=PASS_STRUCTURAL_48_RUN_432_APPLICATION_FLOW_MAPPING;_METADATA_DEFAULT_MISMATCH_RECORDED",
        "REPRESENTATIVE_REPLAY=PASS_3_OF_3_REBUILT_EXECUTED_9_FLOWS_EACH_EXACT_NUMERICAL_MATCH",
        "SAME_SEED_REPEATABILITY=PASS_ZERO_KPI_DELTA_FOR_TWO_MEDIUM_RUNS",
        "INDEPENDENT_REFERENCE=PASS_9_FLOWS_63_METRICS_CONSISTENT",
        "DATASET_REGENERATION_REQUIRED=NO_FOR_CURRENT_FLOWMON_EVIDENCE;CONDITIONAL_FOR_TERMINAL_LOSS_OR_METADATA_REPAIR",
        "SUPPORTED_WIRELESS_CLAIMS=BOUNDED_SYNTHETIC_NS3_44_LTE_EPC_WIFI_80211N_AND_CSMA_LIFI_SURROGATE_REPRODUCIBILITY",
        "UNSUPPORTED_WIRELESS_CLAIMS=5G_NR_PHYSICAL_LIFI_UNIVERSAL_TECHNOLOGY_RANKING_MEASURED_WIRELESS_VALIDATION_ZERO_TERMINAL_LOSS",
        "READY_FOR_MANUSCRIPT_REVISION=YES_WITH_THE_ABOVE_CLAIM_BOUNDARY_AND_METADATA_CAVEATS",
    ]
    (WORKSPACE / "WIRELESS_REVISION_W1_NS3_VALIDATION.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    render_replay_report()
    render_claim_boundary()
    render_primary()
    print("W1 reports rendered")


if __name__ == "__main__":
    main()
