#!/usr/bin/env python3
"""Compare compiled ns-3 LiFi probe output with the independent oracle."""

from __future__ import annotations

import csv
import math
from pathlib import Path

from lifi_reference import LiFiParameters, link_budget


ROOT = Path(__file__).resolve().parent
PROBE = ROOT.parent / "final_runs" / "acceptance_probe" / "lifi_link_probe.csv"
OUT = ROOT / "lifi_reference_comparison.csv"


def main() -> int:
    params = LiFiParameters(fov_rad=math.radians(40.0))
    rows = []
    fields = ["h_los", "received_optical_power_w", "snr", "ber", "per"]
    with PROBE.open(newline="") as stream:
        for record in csv.DictReader(stream):
            ref = link_budget(
                params,
                float(record["distance_m"]),
                float(record["irradiance_angle_rad"]),
                float(record["incidence_angle_rad"]),
            )
            row = {"geometry": record["geometry"], "status": "PASS"}
            for field in fields:
                ns3_value = float(record[field])
                ref_field = {
                    "h_los": "h_los",
                    "received_optical_power_w": "p_r_w",
                    "snr": "snr",
                    "ber": "ber",
                    "per": "per",
                }[field]
                reference = float(ref[ref_field])
                absolute = abs(ns3_value - reference)
                relative = absolute / abs(reference) if reference != 0.0 else absolute
                passed = absolute <= 1.0e-12 or relative <= 1.0e-10
                if not passed:
                    row["status"] = "FAIL"
                row[f"{field}_ns3"] = f"{ns3_value:.17g}"
                row[f"{field}_reference"] = f"{reference:.17g}"
                row[f"{field}_abs_error"] = f"{absolute:.17g}"
                row[f"{field}_rel_error"] = f"{relative:.17g}"
            rows.append(row)
    with OUT.open("w", newline="") as stream:
        fieldnames = list(rows[0]) if rows else ["geometry", "status"]
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    checks = len(rows) * len(fields)
    failures = sum(row["status"] == "FAIL" for row in rows)
    report = ROOT / "lifi_reference_comparison_report.md"
    report.write_text(
        "# ns-3 LiFi probe versus independent reference\n\n"
        f"Compared {len(rows)} geometries and {checks} exported quantities (`H_LOS`, received power, SNR, BER, PER).\n\n"
        f"Result: **{'PASS' if failures == 0 else 'FAIL'}**; geometry-level failures: {failures}.\n\n"
        "The comparison is an equation-implementation check. It is not calibration or physical-testbed validation.\n",
        encoding="utf-8",
    )
    print(f"probe checks={checks}, geometry failures={failures}")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
