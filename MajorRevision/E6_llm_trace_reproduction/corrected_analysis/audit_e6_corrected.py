"""Audit archived corrected E6 data and regenerate manuscript result figures.

No LLM calls or simulations. Configuration expectations are specified independently
of observed records. Run with Python 3.12 and matplotlib; no archive extraction.
"""
from __future__ import annotations

import csv
import hashlib
import io
import itertools
import json
import math
import platform
import re
import statistics
import tarfile
import time
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
E6 = ROOT / "revision_experiments/E6_llm_trace_reproduction"
OUT = E6 / "corrected_analysis"
COMMIT = "82914127b70acf3b220bc09a56a179cb7abd1252"
DESTINATIONS = ["bradley stoke", "froxfield", "reading", "powergate"]
MODULATIONS = ["QPSK", "16QAM"]
POWERS = [-6.5, -6.0, -5.5]
KEY = ["source", "destination", "transmitter_type", "modulation",
       "channel_pattern", "launch_power_dbm"]
METRICS = ["gsnr_signal_bw_db", "osnr_signal_bw_db"]
ARCHIVES = {
    "E6_corrected_second_round_20260914.tar.gz": "6d62aedad432140cefb06a652f52fe6e4ecac26bc8d42ac758f4e38db836e52e",
    "E6_completed_reproduction_20260913_134829_038619.tar.gz": "d233ca08f2075084a75460a899b38ae36145349fad63db0d5056fe30ad2c7720",
}


def write_csv(name, rows, fields=None):
    with (OUT / name).open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields or list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def expected_configurations():
    return [("bristol", destination, "voyager", modulation, f"{pattern:08b}", power)
            for destination, modulation, pattern, power in itertools.product(
                DESTINATIONS, MODULATIONS, range(256), POWERS)]


def key(record):
    s = record["scenario"]
    return (s["source"], s["destination"], s["transmitter_type"],
            s["modulation"], s["channel_pattern"], float(s["power"]))


def flatten(record):
    s, o = record["scenario"], record["output"]
    return dict(zip(KEY, key(record))) | {
        "scenario_id": s["scenario_id"], "iteration": s["iteration"],
        "status": o["status"], "channels": s["channel_pattern"].count("1"),
        "distance_km": s["distance"], "slot_width_ghz": s["min_spacing_ghz"],
        **{m: o.get("metrics", {}).get(m) for m in METRICS},
    }


def make_figures(rows):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch
    plt.rcParams.update({"font.size": 9, "axes.spines.top": False,
                         "axes.spines.right": False, "pdf.fonttype": 42})
    colours = ["#1976d2", "#2e7d32", "#ef6c00", "#9c3848"]
    valid = [r for r in rows if r["status"] == "ok"]
    fig, axs = plt.subplots(2, 2, figsize=(11.4, 7.0), layout="constrained")
    ax = axs[0, 0]
    ax.bar([0, 1], [6144, 6144], color="#1976d2", label="Unique configurations")
    ax.bar([0, 1], [0, 2048], bottom=[6144, 6144], color="#bccbd6", label="Repeated configurations")
    ax.set_xticks([0, 1], ["Deterministic enumeration", "Corrected E6 execution history"])
    ax.tick_params(axis="x", labelsize=8)
    ax.set_ylabel("Configuration records")
    ax.set_ylim(0, 10600)
    ax.set_title("(a) Coverage and repeated configurations", loc="left")
    ax.text(0, 6300, "6,144", ha="center")
    ax.text(1, 8350, "8,192; 25% repeated", ha="center")
    ax.legend(loc="upper left", fontsize=8, frameon=False)
    ax = axs[0, 1]
    positions, samples = [], []
    for i, destination in enumerate(DESTINATIONS):
        for j, modulation in enumerate(MODULATIONS):
            positions.append(3*i+j+1)
            samples.append([r[METRICS[0]] for r in valid if r["destination"] == destination
                            and r["modulation"] == modulation and r["launch_power_dbm"] == -5.5])
    boxes = ax.boxplot(samples, positions=positions, widths=.65, patch_artist=True, showfliers=False)
    for i, box in enumerate(boxes["boxes"]):
        box.set_facecolor(["#42b7c8", "#f39c34"][i % 2])
    ax.set_xticks([1.5, 4.5, 7.5, 10.5], ["Bradley\nStoke", "Froxfield", "Reading", "Powergate"])
    ax.set_ylabel("GSNR, signal bandwidth (dB)")
    ax.set_title("(b) Joint format/slot configuration at −5.5 dBm", loc="left")
    ax.legend(handles=[Patch(color="#42b7c8", label="QPSK / 37.5 GHz"),
                       Patch(color="#f39c34", label="16QAM / 50 GHz")], fontsize=8, frameon=False)
    for destination, colour in zip(DESTINATIONS, colours):
        selected = [r for r in valid if r["destination"] == destination]
        means = [statistics.mean(r[METRICS[0]] for r in selected if r["launch_power_dbm"] == p) for p in POWERS]
        axs[1, 0].plot(POWERS, [v-means[-1] for v in means], "o-", color=colour, label=destination.title())
        loading = [statistics.mean(r[METRICS[0]] for r in selected
                                  if r["launch_power_dbm"] == -5.5 and r["modulation"] == "QPSK"
                                  and r["channels"] == c) for c in range(1, 9)]
        axs[1, 1].plot(range(1, 9), loading, "o-", color=colour, label=destination.title())
    ax = axs[1, 0]
    ax.set_title("(c) Corrected launch-power sweep", loc="left")
    ax.set_xlabel("Launch power (dBm)")
    ax.set_ylabel("Mean ΔGSNR relative to −5.5 dBm (dB)")
    ax.set_xticks(POWERS)
    ax.axhline(0, color="#888888", linewidth=.7)
    ax = axs[1, 1]
    ax.set_title("(d) QPSK / 37.5 GHz at −5.5 dBm", loc="left")
    ax.set_xlabel("Active WDM channels")
    ax.set_ylabel("Mean GSNR, signal bandwidth (dB)")
    ax.set_xticks(range(1, 9))
    for ax in axs.flat:
        ax.grid(axis="y", alpha=.2)
        ax.set_axisbelow(True)
    for ax in axs[1]:
        ax.legend(fontsize=8, frameon=False)
    for ext in ["png", "pdf"]:
        fig.savefig(OUT / f"usecase1_corrected.{ext}", dpi=400)
    plt.close(fig)
    fig, axs = plt.subplots(1, 2, figsize=(10, 3.6), layout="constrained")
    for ax, metric, title in zip(axs, METRICS, ["GSNR", "OSNR"]):
        for destination, colour in zip(DESTINATIONS, colours):
            means = [statistics.mean(r[metric] for r in valid if r["destination"] == destination
                                     and r["launch_power_dbm"] == p) for p in POWERS]
            ax.plot(POWERS, means, "o-", color=colour, label=destination.title())
        ax.set_xlabel("Launch power (dBm)")
        ax.set_ylabel(f"Mean {title}, signal bandwidth (dB)")
        ax.set_xticks(POWERS)
        ax.grid(alpha=.2)
        ax.legend(fontsize=8, frameon=False)
    for ext in ["png", "pdf"]:
        fig.savefig(OUT / f"corrected_power_metrics.{ext}", dpi=400)
    plt.close(fig)


def main():
    OUT.mkdir(exist_ok=True)
    for name, expected in ARCHIVES.items():
        assert hashlib.sha256((E6 / name).read_bytes()).hexdigest() == expected, name
    requests, warnings = {}, Counter()
    with tarfile.open(E6 / next(iter(ARCHIVES)), "r|gz") as archive:
        for member in archive:
            if not member.isfile():
                continue
            if member.name == "replay_manifest.json":
                manifest = json.load(archive.extractfile(member))
            elif member.name == "combined_corrected_records.jsonl":
                records = [json.loads(line) for line in archive.extractfile(member) if line.strip()]
            elif member.name.startswith("gnpy_runtime/") and member.name.endswith("_request.json"):
                d = json.load(archive.extractfile(member))
                requests[d["scenario_id"]] = d
            elif member.name.startswith("gnpy_runtime/") and member.name.endswith("_result.json"):
                d = json.load(archive.extractfile(member))
                warnings["result_files"] += 1
                stderr = d.get("stderr", "")
                for label, pattern in {
                    "edfa_below_min_gain": r"effective gain.*?below user specified amplifier",
                    "roadm_target_power_unmet": r"maximum target power .*? can not be met",
                }.items():
                    found = re.findall(pattern, stderr, re.I | re.S)
                    warnings[label + "_occurrences"] += len(found)
                    warnings[label + "_affected_files"] += bool(found)
    for filename, expected in manifest["source_file_sha256"].items():
        # Git blobs use LF; the Windows checkout may use CRLF.
        raw = (ROOT / filename).read_bytes().replace(b"\r\n", b"\n")
        assert hashlib.sha256(raw).hexdigest() == expected, filename
    assert len(records) == 8192
    assert len({r["scenario"]["scenario_id"] for r in records}) == 8192
    second = [r for r in records if r["scenario"]["iteration"] == 2]
    assert len(second) == 6144
    durations = []
    for _ in range(31):
        start = time.perf_counter()
        expected_list = expected_configurations()
        durations.append(time.perf_counter() - start)
    expected = set(expected_list)
    observed = {key(r) for r in second}
    assert len(expected) == 6144 and observed == expected
    assert {key(r) for r in records} == expected
    assert Counter(r["output"]["status"] for r in second) == {"ok": 6120, "no_signal": 24}
    assert len(requests) == 6120
    for r in second:
        s, o = r["scenario"], r["output"]
        assert (o["status"] == "no_signal") == (s["channel_pattern"] == "00000000")
        if o["status"] == "ok":
            request = requests[s["scenario_id"]]
            assert s["power"] == request["launch_power_dbm"] == o["metrics"]["launch_power_dbm"]
            command = request["cli_command"]
            assert float(command[command.index("-po") + 1]) == s["power"]
            assert request["channel_pattern"] == s["channel_pattern"]
            assert all(math.isfinite(o["metrics"][m]) for m in METRICS)
    rows = sorted([flatten(r) for r in second], key=lambda r: tuple(r[k] for k in KEY))
    write_csv("corrected_unique_configurations.csv", rows)
    write_csv("deterministic_expected_configurations.csv", [dict(zip(KEY, k)) for k in sorted(expected)])
    write_csv("enumeration_timings.csv", [{"repeat": i+1, "enumeration_seconds": d}
                                        for i, d in enumerate(durations)])
    counts = Counter(key(r) for r in records)
    write_csv("repeated_configurations.csv", [dict(zip(KEY, k)) | {"execution_count": n}
                                              for k, n in sorted(counts.items()) if n > 1])
    summaries = []
    for destination, modulation, power in itertools.product(DESTINATIONS, MODULATIONS, POWERS):
        group = [r for r in rows if r["destination"] == destination and r["modulation"] == modulation
                 and r["launch_power_dbm"] == power and r["status"] == "ok"]
        summaries.append({"destination": destination, "modulation": modulation, "launch_power_dbm": power,
                          "ok_configurations": len(group), **{f"mean_{m}": statistics.mean(r[m] for r in group) for m in METRICS}})
    write_csv("power_summary_by_route_and_format.csv", summaries)
    pairs = defaultdict(dict)
    for r in rows:
        if r["status"] == "ok":
            pairs[(r["destination"], r["channel_pattern"], r["launch_power_dbm"])][r["modulation"]] = r[METRICS[0]]
    differences = [abs(p["QPSK"]-p["16QAM"]) for p in pairs.values()]
    with tarfile.open(E6 / list(ARCHIVES)[1], "r|gz") as archive:
        for member in archive:
            if member.isfile() and member.name.endswith("/llm_trace/call_summary.csv"):
                calls = list(csv.DictReader(io.StringIO(archive.extractfile(member).read().decode("utf-8"))))
                break
    assert len(calls) == 6 and all(c["status"] == "success" for c in calls)
    write_csv("new_run_call_summary.csv", calls)
    summary = {
        "evidence_commit": COMMIT, "archive_sha256": ARCHIVES,
        "python": platform.python_version(), "platform": platform.platform(),
        "execution_records": len(records), "unique_configurations": len(observed),
        "duplicate_records_beyond_first": len(records)-len(observed), "duplicate_rate": .25,
        "expected_missing": len(expected-observed), "unexpected_extra": len(observed-expected),
        "set_precision": 1.0, "set_recall": 1.0,
        "second_round_status_counts": dict(Counter(r["output"]["status"] for r in second)),
        "combined_status_counts": dict(Counter(r["output"]["status"] for r in records)),
        "scenario_request_cli_metric_power_checks": len(requests), "power_mismatches": 0,
        "no_signal_cases_without_cli": 24,
        "enumeration_microbenchmark_repeats": 31,
        "enumeration_seconds_median": statistics.median(durations),
        "enumeration_seconds_min": min(durations), "enumeration_seconds_max": max(durations),
        "timing_scope": "Configuration tuple generation only; excludes set comparison, I/O and GNPy; not independent LLM trials.",
        "new_run_llm_calls": 6, "new_run_tokens": sum(int(c["total_tokens"]) for c in calls),
        "new_run_api_latency_seconds": sum(float(c["latency_seconds"]) for c in calls),
        "new_run_estimated_cost_usd": sum(float(c["estimated_cost_usd"]) for c in calls),
        "earlier_interrupted_attempt": {"calls": 2, "tokens": 4057, "estimated_cost_usd": .0009339,
                                       "source": "revision_documents/09_E6_20260913_new_run_trace_report.md"},
        "known_two_invocation_estimated_cost_usd": round(sum(float(c["estimated_cost_usd"]) for c in calls)+.0009339, 8),
        "corrected_replay_new_llm_calls": 0,
        "corrected_replay_seconds": (datetime.fromisoformat(manifest["completed_at_utc"])-datetime.fromisoformat(manifest["started_at_utc"])).total_seconds(),
        "corrected_result_warnings": dict(warnings),
        "joint_format_slot_pairs": len(differences), "joint_format_slot_mean_abs_gsnr_difference_db": statistics.mean(differences),
        "joint_format_slot_max_abs_gsnr_difference_db": max(differences),
        "limitations": ["One new LLM reproduction with manual recovery, not independent repeated trials.",
                        "Corrected replay reuses saved model responses; old Reflection 2 is not an evaluation of corrected data.",
                        "The historical E5 96-case numerical comparison is not independent validation of the corrected E6 sweep.",
                        "Scenario means equally weight configurations, then average their active-channel metrics; no_signal is excluded."]}
    (OUT / "audit_summary.json").write_text(json.dumps(summary, indent=2)+"\n", encoding="utf-8")
    write_csv("corrected_baseline_comparison.csv", [
        {"method": "Deterministic enumerator", "simulation_executions": 0, "unique_configurations": 6144,
         "duplicate_rate": 0, "set_precision": 1, "set_recall": 1, "llm_calls": 0,
         "api_cost_usd": 0, "enumeration_seconds_median": statistics.median(durations)},
        {"method": "Corrected E6 execution history", "simulation_executions": 8192, "unique_configurations": 6144,
         "duplicate_rate": .25, "set_precision": 1, "set_recall": 1, "llm_calls": 6,
         "api_cost_usd": summary["new_run_estimated_cost_usd"], "enumeration_seconds_median": "not_measured"}])
    make_figures(rows)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
