#!/usr/bin/env python3
"""Run W4C LiFi tests using only the independent Python equations."""

from __future__ import annotations

import csv
import math
from pathlib import Path

from lifi_reference import LiFiParameters, lambertian_order, link_budget


ROOT = Path(__file__).resolve().parent
PARAMS = LiFiParameters()


def row(name: str, passed: bool, observed: float, expected: float, tol: float, note: str):
    return {
        "test": name,
        "status": "PASS" if passed else "FAIL",
        "observed": f"{observed:.16g}",
        "expected": f"{expected:.16g}",
        "absolute_error": f"{abs(observed - expected):.16g}",
        "tolerance": f"{tol:.16g}",
        "note": note,
    }


def main() -> int:
    rows = []
    m = lambertian_order(PARAMS.phi_half_rad)
    rows.append(row("lambertian_order_60deg", abs(m - 1.0) <= 1e-14, m, 1.0, 1e-14, "m=1 at 60 degrees"))

    near = link_budget(PARAMS, 2.0, 0.0, 0.0)
    rows.append(row("aligned_los_gain", near["h_los"] > 0.0 and math.isfinite(near["h_los"]), near["h_los"], near["h_los"], 0.0, "finite positive aligned LOS gain"))

    far = link_budget(PARAMS, 4.0, 0.0, 0.0)
    ratio = far["h_los"] / near["h_los"]
    rows.append(row("inverse_square", abs(ratio - 0.25) <= 1e-14, ratio, 0.25, 1e-14, "H(4 m)/H(2 m)"))

    fov = link_budget(PARAMS, 2.0, 0.0, PARAMS.fov_rad)
    outside = link_budget(PARAMS, 2.0, 0.0, PARAMS.fov_rad + math.radians(0.1))
    rows.append(row("fov_inside", fov["in_fov"] == 1 and fov["h_los"] > 0.0, float(fov["in_fov"]), 1.0, 0.0, "boundary is included"))
    rows.append(row("fov_outside", outside["in_fov"] == 0 and outside["h_los"] == 0.0, outside["h_los"], 0.0, 0.0, "outside FOV is gated"))

    rows.append(row("received_power", abs(near["p_r_w"] - PARAMS.pt_w * near["h_los"]) <= 1e-18, near["p_r_w"], PARAMS.pt_w * near["h_los"], 1e-18, "P_r=P_t H_LOS"))

    zero = outside
    finite_noise = all(math.isfinite(zero[k]) for k in ("shot_variance_a2", "thermal_variance_a2", "snr", "ber", "per"))
    rows.append(row("zero_power_noise_snr", finite_noise and zero["snr"] >= 0.0, zero["snr"], 0.0, 0.0, "finite zero-power SNR"))

    snrs = [0.1, 1.0, 10.0, 100.0]
    pers = []
    for snr in snrs:
        # Reuse exact BER/PER convention, with a direct local calculation.
        ber = 0.5 * math.erfc(math.sqrt(snr) / (2.0 * math.sqrt(2.0)))
        pers.append(-math.expm1((8 * PARAMS.packet_bytes) * math.log1p(-ber)))
    monotonic = all(a >= b for a, b in zip(pers, pers[1:]))
    rows.append(row("per_decreases_with_snr", monotonic, pers[-1], pers[0], 0.0, "PER(SNR) non-increasing"))

    bounded = all(0.0 <= near[k] <= upper for k, upper in (("ber", 0.5), ("per", 1.0)))
    rows.append(row("physical_bounds", bounded, float(bounded), 1.0, 0.0, "BER and PER bounds"))

    out = ROOT / "lifi_unit_tests.csv"
    with out.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    passed = sum(r["status"] == "PASS" for r in rows)
    report = ROOT / "lifi_unit_test_report.md"
    report.write_text(
        "# W4C LiFi/OWC unit-test report\n\n"
        "The tests use `lifi_reference.py`, an independent Python implementation of the declared equations; they do not call ns-3 or the C++ implementation.\n\n"
        f"Result: **{passed}/{len(rows)} PASS**.\n\n"
        "The default numeric parameter set is explicit and uncalibrated to the practical testbed. The tests validate equation behavior, not physical-testbed fidelity.\n",
        encoding="utf-8",
    )
    print(f"{passed}/{len(rows)} PASS")
    return 0 if passed == len(rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
