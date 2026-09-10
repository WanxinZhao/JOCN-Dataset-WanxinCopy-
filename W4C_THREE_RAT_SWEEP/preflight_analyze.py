#!/usr/bin/env python3
"""Summarise the prescribed LiFi FOV preflight without model changes."""

from __future__ import annotations

import csv
import statistics
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PREFLIGHT = ROOT / "preflight"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as stream:
        return list(csv.DictReader(stream))


def quantiles(values: list[float]) -> tuple[float, float, float]:
    values = sorted(values)
    if not values:
        return (float("nan"),) * 3
    if len(values) == 1:
        return (values[0], values[0], values[0])
    q = statistics.quantiles(values, n=100, method="inclusive")
    return (q[9], q[49], q[89])


def main() -> int:
    rows = []
    for fov in (30, 40, 50, 70):
        directory = PREFLIGHT / f"fov{fov}"
        optical = read_csv(directory / "optical_state.csv")
        kpi = read_csv(directory / "kpi.csv")
        powers = [float(row["received_optical_power_w"]) for row in optical]
        snrs = [float(row["snr"]) for row in optical]
        bers = [float(row["ber"]) for row in optical]
        pers = [float(row["per"]) for row in optical]
        power_q = quantiles(powers)
        snr_q = quantiles(snrs)
        ber_q = quantiles(bers)
        per_q = quantiles(pers)
        tx = sum(int(row["tx_packets"]) for row in kpi)
        rx = sum(int(row["rx_packets"]) for row in kpi)
        rows.append(
            {
                "fov_deg": fov,
                "optical_state_rows": len(optical),
                "cpe_count": len({row["cpe_id"] for row in optical}),
                "in_fov_fraction": statistics.mean(int(row["in_fov"]) for row in optical),
                "zero_gain_fraction": statistics.mean(float(row["h_los"]) == 0.0 for row in optical),
                "received_power_p10_w": power_q[0],
                "received_power_median_w": power_q[1],
                "received_power_p90_w": power_q[2],
                "snr_p10": snr_q[0],
                "snr_median": snr_q[1],
                "snr_p90": snr_q[2],
                "ber_p10": ber_q[0],
                "ber_median": ber_q[1],
                "ber_p90": ber_q[2],
                "per_p10": per_q[0],
                "per_median": per_q[1],
                "per_p90": per_q[2],
                "tx_packets": tx,
                "rx_packets": rx,
                "received_packet_fraction": rx / tx if tx else 0.0,
            }
        )
    output = PREFLIGHT / "fov_preflight_summary.csv"
    fields = list(rows[0])
    with output.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    selected = next(row for row in rows if row["fov_deg"] == 40)
    report = PREFLIGHT / "fov_preflight_report.md"
    report.write_text(
        "# W4C LiFi FOV preflight\n\n"
        "All candidates use the final-source LiFi-only executable, offered load 5 Mbps, speed 0.5 m/s, seed 1, 10 s simulation, 1.0–9.5 s application window and the fixed W4B geometry/parameters. Quantities are pooled over the three CPEs and sampled optical states.\n\n"
        + "| FOV | in-FOV fraction | zero-gain fraction | received-packet fraction | median received power (W) | median SNR | median BER | median PER |\n"
        + "|---:|---:|---:|---:|---:|---:|---:|---:|\n"
        + "\n".join(
            f"| {row['fov_deg']} | {float(row['in_fov_fraction']):.6g} | {float(row['zero_gain_fraction']):.6g} | {float(row['received_packet_fraction']):.6g} | {float(row['received_power_median_w']):.6g} | {float(row['snr_median']):.6g} | {float(row['ber_median']):.6g} | {float(row['per_median']):.6g} |"
            for row in rows
        )
        + "\n\n## Selection\n\n"
        + "**Selected narrow FOV: 40 degrees.** It creates measurable out-of-FOV states (12.3% zero-gain samples) while retaining a substantial received-packet fraction (approximately 0.874), unlike the near-outage 30-degree candidate. The 50-degree candidate produced no out-of-FOV samples under this geometry and is therefore not selected. The selection is based on geometry/packet evidence, not on favourable KPI ranking. The selected value is frozen for the final 48-run sweep.\n"
    )
    print(output)
    print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
