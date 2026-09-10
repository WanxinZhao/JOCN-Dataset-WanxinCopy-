# W4C LiFi FOV preflight

All candidates use the final-source LiFi-only executable, offered load 5 Mbps, speed 0.5 m/s, seed 1, 10 s simulation, 1.0–9.5 s application window and the fixed W4B geometry/parameters. Quantities are pooled over the three CPEs and sampled optical states.

| FOV | in-FOV fraction | zero-gain fraction | received-packet fraction | median received power (W) | median SNR | median BER | median PER |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 30 | 0.638889 | 0.361111 | 0.638139 | 0.000446944 | 2.27229e+09 | 0 | 0 |
| 40 | 0.876984 | 0.123016 | 0.873876 | 0.000270432 | 1.35497e+09 | 0 | 0 |
| 50 | 1 | 0 | 1 | 0.000190408 | 9.39528e+08 | 0 | 0 |
| 70 | 1 | 0 | 1 | 0.000126538 | 6.08609e+08 | 0 | 0 |

## Selection

**Selected narrow FOV: 40 degrees.** It creates measurable out-of-FOV states (12.3% zero-gain samples) while retaining a substantial received-packet fraction (approximately 0.874), unlike the near-outage 30-degree candidate. The 50-degree candidate produced no out-of-FOV samples under this geometry and is therefore not selected. The selection is based on geometry/packet evidence, not on favourable KPI ranking. The selected value is frozen for the final 48-run sweep.
