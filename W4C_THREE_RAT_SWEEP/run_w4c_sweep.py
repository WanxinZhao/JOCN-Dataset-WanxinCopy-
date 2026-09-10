#!/usr/bin/env python3
"""Run exactly the frozen 4x2x2x3 W4C integrated sweep."""

from __future__ import annotations

import argparse
import csv
import os
import subprocess
import time
from pathlib import Path


LOADS = (2.0, 5.0, 10.0, 20.0)
SPEEDS = (0.5, 3.0)
FOVS = (40.0, 70.0)
SEEDS = (1, 2, 3)
ROOT = Path(__file__).resolve().parent


def fmt(value: float) -> str:
    return str(value).replace(".", "p")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--binary",
        default=os.environ.get("NS3_W4C_BINARY"),
        help="path to the built ns-3.44 three_rat_smoke binary (or set NS3_W4C_BINARY)",
    )
    parser.add_argument("--output-root", default=str(ROOT / "runs"))
    parser.add_argument("--status-file", default=str(ROOT / "sweep_status.csv"))
    parser.add_argument("--only", nargs="*", help="optional exact run keys")
    args = parser.parse_args()
    if not args.binary:
        parser.error("--binary or NS3_W4C_BINARY is required")

    output_root = Path(args.output_root)
    output_root.mkdir(parents=True, exist_ok=True)
    status_path = Path(args.status_file)
    status_path.parent.mkdir(parents=True, exist_ok=True)
    expected = []
    for load in LOADS:
        for speed in SPEEDS:
            for fov in FOVS:
                for seed in SEEDS:
                    run_key = f"load{fmt(load)}_speed{fmt(speed)}_fov{fmt(fov)}_seed{seed}"
                    expected.append((run_key, load, speed, fov, seed))
    selected = set(args.only) if args.only else {item[0] for item in expected}
    rows = []
    for run_key, load, speed, fov, seed in expected:
        if run_key not in selected:
            continue
        output_dir = output_root / run_key
        if output_dir.exists():
            raise SystemExit(f"refusing to overwrite existing run directory: {run_key}")
        output_dir.mkdir(parents=True, exist_ok=False)
        command = [
            args.binary,
            "--mode=integrated",
            f"--outputDir={output_dir}",
            "--simTime=10s",
            "--appStart=1s",
            "--appStop=9.5s",
            f"--offeredMbps={load}",
            f"--speed={speed}",
            f"--fovDeg={fov}",
            f"--seed={seed}",
            "--run=1",
        ]
        started = time.monotonic()
        result = subprocess.run(command, capture_output=True, text=True, check=False)
        elapsed = time.monotonic() - started
        (output_dir / "run.log").write_text(
            "command=" + " ".join(command) + "\n"
            + f"return_code={result.returncode}\n"
            + f"elapsed_seconds={elapsed:.6f}\n"
            + "stdout:\n" + result.stdout
            + "stderr:\n" + result.stderr,
            encoding="utf-8",
        )
        runtime_summary = output_dir / "runtime_summary.csv"
        matched = ""
        if runtime_summary.exists():
            text = runtime_summary.read_text(encoding="utf-8").splitlines()
            if len(text) > 1:
                matched = text[1].split(",")[-1]
        status = "PASS" if result.returncode == 0 and matched == "9" else "FAIL"
        rows.append(
            {
                "run_id": run_key,
                "offered_load_mbps": load,
                "mobility_speed_mps": speed,
                "lifi_fov_deg": fov,
                "seed": seed,
                "run_number": 1,
                "status": status,
                "return_code": result.returncode,
                "matched_application_flows": matched,
                "elapsed_seconds": f"{elapsed:.6f}",
                "source_directory": str(output_dir),
            }
        )
        print(run_key, status, f"{elapsed:.2f}s", flush=True)
    with status_path.open("w", newline="") as stream:
        fields = list(rows[0]) if rows else ["run_id", "status"]
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    failed = [row["run_id"] for row in rows if row["status"] != "PASS"]
    expected_selected = len(selected)
    print(f"completed={len(rows)}/{expected_selected} failed={len(failed)}")
    if failed:
        print("failed_runs=" + ",".join(failed))
    return 0 if len(rows) == expected_selected and not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
