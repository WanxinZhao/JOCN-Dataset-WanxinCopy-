#!/usr/bin/env python3
"""Independent mathematical reference for the W4C LOS LiFi/OWC model.

This file deliberately has no ns-3 dependency.  It is used both as a small
link-budget oracle and by the deterministic unit-test driver.
All angles are radians; distances are metres; powers are watts; currents are
ampere; bandwidth is hertz; resistance is ohm; rates are bit/s.
"""

from __future__ import annotations

import math
from dataclasses import dataclass


Q_E = 1.602176634e-19  # C
K_B = 1.380649e-23  # J/K


@dataclass(frozen=True)
class LiFiParameters:
    pt_w: float = 10.0
    phi_half_rad: float = math.radians(60.0)
    area_m2: float = 1.0e-4
    responsivity_a_per_w: float = 0.5
    fov_rad: float = math.radians(70.0)
    concentrator_index: float = 1.5
    filter_gain: float = 1.0
    background_current_a: float = 5.1e-6
    bandwidth_hz: float = 3.0e5
    temperature_k: float = 295.0
    load_resistance_ohm: float = 1.0e6
    packet_bytes: int = 1024
    nominal_rate_bps: float = 100.0e6


def clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


def q_function(x: float) -> float:
    return 0.5 * math.erfc(x / math.sqrt(2.0))


def lambertian_order(phi_half_rad: float) -> float:
    if not (0.0 < phi_half_rad < math.pi / 2.0):
        raise ValueError("half-power semi-angle must be in (0, pi/2)")
    return -math.log(2.0) / math.log(math.cos(phi_half_rad))


def link_budget(
    params: LiFiParameters,
    distance_m: float,
    irradiance_rad: float,
    incidence_rad: float,
) -> dict[str, float | int]:
    if distance_m <= 0.0:
        raise ValueError("distance must be positive")
    m = lambertian_order(params.phi_half_rad)
    in_fov = int(0.0 <= incidence_rad <= params.fov_rad)
    if in_fov:
        concentrator_gain = params.concentrator_index**2 / math.sin(params.fov_rad) ** 2
        h_los = (
            (m + 1.0)
            * params.area_m2
            / (2.0 * math.pi * distance_m**2)
            * math.cos(irradiance_rad) ** m
            * params.filter_gain
            * concentrator_gain
            * math.cos(incidence_rad)
        )
        h_los = max(0.0, h_los)
    else:
        h_los = 0.0
    p_r = params.pt_w * h_los
    signal_current = params.responsivity_a_per_w * p_r
    shot_variance = (
        2.0
        * Q_E
        * (signal_current + params.background_current_a)
        * params.bandwidth_hz
    )
    thermal_variance = (
        4.0
        * K_B
        * params.temperature_k
        * params.bandwidth_hz
        / params.load_resistance_ohm
    )
    denominator = shot_variance + thermal_variance
    snr = signal_current**2 / denominator if denominator > 0.0 else 0.0
    ber = clamp(q_function(math.sqrt(max(0.0, snr)) / 2.0), 0.0, 0.5)
    # expm1/log1p preserve finite behaviour for both very small and very
    # large packet error probabilities.
    per = -math.expm1((8 * params.packet_bytes) * math.log1p(-ber))
    per = clamp(per, 0.0, 1.0)
    return {
        "m": m,
        "in_fov": in_fov,
        "h_los": h_los,
        "p_r_w": p_r,
        "signal_current_a": signal_current,
        "shot_variance_a2": shot_variance,
        "thermal_variance_a2": thermal_variance,
        "snr": snr,
        "ber": ber,
        "per": per,
    }


if __name__ == "__main__":
    print(link_budget(LiFiParameters(), 2.0, 0.0, 0.0))
