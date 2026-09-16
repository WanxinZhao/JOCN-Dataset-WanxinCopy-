#!/usr/bin/env python3
"""Compile, run, and compare the hand-written ns-3 reference."""

from __future__ import annotations

import csv
import json
import math
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import archive_audit as audit
import run_replays as replays


WORKSPACE = Path("/home/ubuntu/Desktop/LLM Driven wireless environment generation")
OUT = WORKSPACE / "W1_NS3_VALIDATION" / "independent_reference"
SOURCE = OUT / "reference.cc"
BINARY = OUT / "reference"
RESULTS = OUT / "results"
GENERATED_RESULTS = WORKSPACE / "W1_NS3_VALIDATION" / "replays" / "medium_load_high_mobility" / "fresh_results" / "flowmon.xml"


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    fields: list[str] = []
    for row in rows:
        for field in row:
            if field not in fields:
                fields.append(field)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def run_reference() -> dict[str, object]:
    compile_cmd = replays.compile_command(SOURCE, BINARY)
    compile_result = subprocess.run(compile_cmd, cwd=replays.NS3_ROOT, text=True, capture_output=True, check=False)
    (OUT / "compile.log").write_text(
        "COMMAND\n" + " ".join(compile_cmd) + "\n\nSTDOUT\n" + compile_result.stdout +
        "\nSTDERR\n" + compile_result.stderr,
        encoding="utf-8",
    )
    if compile_result.returncode != 0:
        raise RuntimeError(f"reference compile failed; see {OUT / 'compile.log'}")
    RESULTS.mkdir(parents=True, exist_ok=True)
    output_arg = RESULTS.relative_to(WORKSPACE)
    run_cmd = [str(BINARY), f"--outputDir={output_arg}"]
    run_result = subprocess.run(run_cmd, cwd=WORKSPACE, text=True, capture_output=True, check=False)
    (OUT / "run.log").write_text(
        "COMMAND\n" + " ".join(run_cmd) + "\n\nSTDOUT\n" + run_result.stdout +
        "\nSTDERR\n" + run_result.stderr,
        encoding="utf-8",
    )
    if run_result.returncode != 0:
        raise RuntimeError(f"reference run failed; see {OUT / 'run.log'}")
    return {"compile_command": compile_cmd, "compile_returncode": compile_result.returncode, "run_command": run_cmd, "run_returncode": run_result.returncode}


def parse(path: Path) -> dict[tuple[str, str], dict[str, object]]:
    audit.CURRENT_SIM_TIME = 10.0
    rows, _mapping = audit.parse_flowmon(path.read_text(encoding="utf-8"))
    result: dict[tuple[str, str], dict[str, object]] = {}
    for row in rows:
        if row["is_application"]:
            result[(row["access_type"], row["cpe"])] = row
    return result


def topology_compare() -> tuple[list[dict[str, object]], dict[str, object]]:
    audit.CURRENT_SIM_TIME = 10.0
    generated_rows, generated_mapping = audit.parse_flowmon(GENERATED_RESULTS.read_text(encoding="utf-8"))
    generated_app = {
        (row["access_type"], row["cpe"]): row
        for row in generated_rows
        if row["is_application"]
    }
    with (RESULTS / "reference_manifest.csv").open(newline="", encoding="utf-8") as handle:
        reference_manifest = list(csv.DictReader(handle))
    reference_declared = {
        (row["declared_access"], row["cpe"]): (row["destination_address"], row["port"])
        for row in reference_manifest
    }
    generated_declared = {
        key: (row["destination_address"], str(row["destination_port"]))
        for key, row in generated_app.items()
    }
    def serialise_declarations(values: dict[tuple[str, str], object]) -> str:
        return json.dumps({f"{access}/{cpe}": value for (access, cpe), value in values.items()}, sort_keys=True, separators=(",", ":"))
    rows: list[dict[str, object]] = []

    def add(check: str, generated: object, reference: object, passed: bool, note: str) -> None:
        rows.append({
            "check": check,
            "generated_value": generated,
            "reference_value": reference,
            "status": "CONSISTENT" if passed else "MATERIALLY_DIFFERENT",
            "note": note,
        })

    add(
        "application_flow_count",
        len(generated_app),
        len(reference_manifest),
        len(generated_app) == len(reference_manifest) == 9,
        "Nine downlink application flows are expected.",
    )
    add(
        "access_cpe_keys",
        json.dumps(sorted(generated_declared), separators=(",", ":")),
        json.dumps(sorted(reference_declared), separators=(",", ":")),
        set(generated_declared) == set(reference_declared),
        "Compared by access branch and CPE.",
    )
    add(
        "destination_addresses_and_ports",
        serialise_declarations(generated_declared),
        serialise_declarations(reference_declared),
        generated_declared == reference_declared,
        "XML classifier destinations are compared with the hand-written manifest.",
    )
    add(
        "three_cpes_per_access",
        json.dumps({access: sorted(cpe for branch, cpe in generated_declared if branch == access) for access in sorted({branch for branch, _ in generated_declared})}, separators=(",", ":")),
        json.dumps({access: sorted(cpe for branch, cpe in reference_declared if branch == access) for access in sorted({branch for branch, _ in reference_declared})}, separators=(",", ":")),
        all(sum(1 for branch, _ in generated_declared if branch == access) == 3 for access in {branch for branch, _ in generated_declared})
        and all(sum(1 for branch, _ in reference_declared if branch == access) == 3 for access in {branch for branch, _ in reference_declared}),
        "Each branch should have CPE1-CPE3.",
    )
    add(
        "flow_id_access_mapping",
        json.dumps({str(flow_id): generated_mapping[flow_id]["access_type"] for flow_id in sorted(generated_mapping) if generated_mapping[flow_id].get("is_application")}, sort_keys=True),
        "Access mapping declared independently by the reference manifest",
        set(generated_app) == set(reference_declared),
        "Numeric FlowMonitor IDs are not used as the comparison key.",
    )
    summary = {
        "checks": len(rows),
        "consistent": sum(row["status"] == "CONSISTENT" for row in rows),
        "materially_different": sum(row["status"] == "MATERIALLY_DIFFERENT" for row in rows),
    }
    return rows, summary


def value(row: dict[str, object], metric: str) -> float:
    if metric == "packet_loss_ratio":
        return float(row["lost_packets"]) / float(row["tx_packets"]) if row["tx_packets"] else 0.0
    return float(row[metric])


def status(metric: str, generated: float, reference: float) -> tuple[str, float | None, float]:
    delta = abs(reference - generated)
    if generated != 0:
        relative = delta / abs(generated)
    else:
        relative = 0.0 if delta == 0 else None
    if metric in {"tx_packets", "rx_packets", "flowmonitor_lost_packets"}:
        tolerance = 0.0
        passed = delta == 0
    elif metric == "packet_loss_ratio":
        tolerance = 1e-12
        passed = delta <= tolerance
    else:
        # A 1% per-flow tolerance with a 1 microsecond floor is used only for
        # the independent implementation comparison; archived XML rounding
        # errors are much smaller than this on application flows.
        tolerance = max(1e-6, 0.01 * abs(generated))
        passed = delta <= tolerance
    return ("CONSISTENT" if passed else "MATERIALLY_DIFFERENT"), relative, tolerance


def compare() -> tuple[list[dict[str, object]], dict[str, object]]:
    generated = parse(GENERATED_RESULTS)
    reference = parse(RESULTS / "flowmon.xml")
    rows: list[dict[str, object]] = []
    metrics = ("tx_packets", "rx_packets", "flowmonitor_lost_packets", "packet_loss_ratio", "throughput_mbps", "mean_delay_ms", "mean_jitter_ms")
    for key in sorted(set(generated) | set(reference)):
        access, cpe = key
        g = generated.get(key)
        r = reference.get(key)
        if g is None or r is None:
            rows.append({"access_type": access, "cpe": cpe, "metric": "flow_presence", "generated_present": g is not None, "reference_present": r is not None, "status": "NOT_COMPARABLE"})
            continue
        for metric in metrics:
            if metric == "tx_packets":
                gv, rv = float(g["tx_packets"]), float(r["tx_packets"])
            elif metric == "rx_packets":
                gv, rv = float(g["rx_packets"]), float(r["rx_packets"])
            elif metric == "flowmonitor_lost_packets":
                gv, rv = float(g["lost_packets"]), float(r["lost_packets"])
            else:
                gv, rv = value(g, metric), value(r, metric)
            decision, relative, tolerance = status(metric, gv, rv)
            rows.append({
                "access_type": access,
                "cpe": cpe,
                "metric": metric,
                "generated_value": gv,
                "reference_value": rv,
                "absolute_delta": abs(rv - gv),
                "relative_delta": relative,
                "tolerance": tolerance,
                "status": decision,
            })
    counts = {}
    for metric in metrics:
        selected = [row for row in rows if row.get("metric") == metric]
        counts[metric] = {
            "records": len(selected),
            "consistent": sum(row.get("status") == "CONSISTENT" for row in selected),
            "materially_different": sum(row.get("status") == "MATERIALLY_DIFFERENT" for row in selected),
            "max_absolute_delta": max((float(row["absolute_delta"]) for row in selected), default=None),
        }
    summary = {
        "generated_flow_count": len(generated),
        "reference_flow_count": len(reference),
        "expected_application_flow_count": 9,
        "all_expected_flows_present": len(generated) == 9 and len(reference) == 9,
        "metric_counts": counts,
        "interpretation": "The comparison is keyed by classifier-derived access_type and CPE, not by FlowMonitor flow ID.",
    }
    return rows, summary


def main() -> None:
    execution = run_reference()
    rows, summary = compare()
    topology_rows, topology_summary = topology_compare()
    summary["topology"] = topology_summary
    summary["execution"] = execution
    write_csv(OUT / "comparison.csv", rows)
    write_csv(OUT / "topology_config_comparison.csv", topology_rows)
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    status_counts = {}
    for row in rows:
        status_counts[row.get("status", "NOT_COMPARABLE")] = status_counts.get(row.get("status", "NOT_COMPARABLE"), 0) + 1
    lines = [
        "# Independent hand-written ns-3 reference report",
        "",
        "The reference is a new fixed-configuration C++ program at " + str(SOURCE) +
        ". It was compiled with the existing ns-3.44 build libraries and run at the medium archived operating point:",
        "",
        "- duration: 10 s",
        "- seed: 2",
        "- offered load: 10 Mbps per application flow",
        "- packet size: 1024 bytes",
        "- mobility speed: 3 m/s",
        "- CSMA LiFi-surrogate rate: 100 Mbps",
        "- three CPEs and three access branches, with nine downlink UDP flows",
        "",
        "## Structural comparison",
        "",
        f"- generated application flows: {summary['generated_flow_count']}",
        f"- reference application flows: {summary['reference_flow_count']}",
        f"- all expected flows present: {summary['all_expected_flows_present']}",
        "- flow comparison key: XML classifier-derived access type and CPE, not the numeric FlowMonitor ID",
        "",
        "## Numerical comparison",
        "",
        "The per-flow tolerance is exact equality for packet counters, 1e-12 for the FlowMonitor loss ratio, and max(1e-6, 1%) for continuous KPIs. The tolerance is a comparison rule, not a claim of physical uncertainty.",
        "",
        f"- status counts: {status_counts}",
        f"- topology/configuration checks: {topology_summary}",
    ]
    for metric, detail in summary["metric_counts"].items():
        lines.append(f"- {metric}: {detail}")
    lines.extend([
        "",
        "## Interpretation",
        "",
        "The hand-written reference independently instantiates the same declared topology, access mapping, application count, and stock ns-3.44 modelling assumptions. A CONSISTENT result means the per-flow value met the stated comparison tolerance. This does not turn the CSMA LiFi surrogate into a physical optical model and does not validate universal cross-technology rankings.",
        "",
        "Evidence files:",
        "",
        f"- source: {SOURCE}",
        f"- generated comparison input: {GENERATED_RESULTS}",
        f"- reference FlowMonitor XML: {RESULTS / 'flowmon.xml'}",
        f"- keyed comparison: {OUT / 'comparison.csv'}",
        f"- topology/configuration comparison: {OUT / 'topology_config_comparison.csv'}",
        f"- execution logs: {OUT / 'compile.log'}, {OUT / 'run.log'}",
    ])
    (OUT / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"summary": summary, "status_counts": status_counts}, indent=2))


if __name__ == "__main__":
    main()
