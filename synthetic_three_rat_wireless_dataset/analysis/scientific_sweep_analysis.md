# Scientific analysis of the synthetic three-RAT dataset

This analysis uses the run as the experimental unit: the three CPE application-flow rows are averaged within each run/branch, and the three seeds are retained as the random-seed replicates for each fixed parameter cell.

## Coverage

- Run-level branch summaries: **144** (48 runs × 3 branches).
- LiFi physical summaries: **144** (48 runs × 3 CPEs).
- Factors: offered load 2/5/10/20 Mbps; mobility 0.5/3.0 m/s; LiFi FOV 40/70°; seeds 1/2/3.

## Q1 — offered load

- **NR:** 20−2 Mbps paired change: throughput 18.4864 Mbps, delay 0.0264963 ms, jitter -0.00642519 ms, FlowMonitor-reported loss ratio 0; 12 paired run units.
- **WiFi80211ax:** 20−2 Mbps paired change: throughput 0.151118 Mbps, delay 1653.88 ms, jitter 2.55907 ms, FlowMonitor-reported loss ratio 0.701271; 12 paired run units.
- **LiFi:** 20−2 Mbps paired change: throughput 15.7256 Mbps, delay -2.31296e-18 ms, jitter 0 ms, FlowMonitor-reported loss ratio 0; 12 paired run units.

Interpretation: the load response is configuration-specific. These paired changes identify whether the declared workload moves the branch toward a different operating regime, but they do not establish a universal capacity ranking.

## Q2 — mobility

- **NR:** 3.0−0.5 m/s paired change: throughput 0 Mbps, delay 0.000593527 ms, jitter 0.000309194 ms, FlowMonitor-reported loss ratio 0; 24 paired run units.
- **WiFi80211ax:** 3.0−0.5 m/s paired change: throughput 0.000182162 Mbps, delay 0.079698 ms, jitter 0.00219447 ms, FlowMonitor-reported loss ratio -0.000246295; 24 paired run units.
- **LiFi:** 3.0−0.5 m/s paired change: throughput -2.57237 Mbps, delay -0.00937 ms, jitter 0 ms, FlowMonitor-reported loss ratio 0; 24 paired run units.

Interpretation: mobility effects are reported empirically under the selected ns-3 channel and mobility implementation; a small paired effect is not evidence that mobility is universally unimportant.

## Q3 — LiFi FOV

- LiFi 40−70° paired change: throughput -2.51721 Mbps, delay -0.00937 ms, jitter 0 ms, FlowMonitor-reported loss ratio 0; 24 paired run units.
- LiFi received-packet fraction (computed from exported tx/rx counters, 40−70°): mean delta -0.299295; 24 paired run units. FlowMonitor-reported loss ratio is kept separate and is not interpreted as terminal loss.
- Optical in_fov_fraction (40−70°): mean delta -0.299306; 72 paired CPE/run observations.
- Optical zero_gain_fraction (40−70°): mean delta 0.299306; 72 paired CPE/run observations.
- Optical distance_mean (40−70°): mean delta 0; 72 paired CPE/run observations.
- Optical H_LOS_mean (40−70°): mean delta 9.26612e-06; 72 paired CPE/run observations.
- Optical received_power_mean (40−70°): mean delta 9.26612e-05; 72 paired CPE/run observations.
- Optical SNR_mean (40−70°): mean delta 4.90029e+08; 72 paired CPE/run observations.
- Optical SNR_min (40−70°): mean delta 2.55523e+08; 72 paired CPE/run observations.
- Optical BER_mean (40−70°): mean delta 0.149653; 72 paired CPE/run observations.
- Optical PER_mean (40−70°): mean delta 0.299306; 72 paired CPE/run observations.

Interpretation: narrowing the FOV is physically expected to reduce geometric acceptance. The preflight and paired summaries should be read through the LOS/FOV equations, not as a calibrated practical LiFi performance claim.

## Q4 — RAT-dependent variation

The branch distribution file reports nonzero ranges and branch-specific means for the run-level KPIs. This establishes that the final dataset contains configuration-dependent RAT variation rather than only a branch label, while not supporting a universal ranking across technologies.

## Q5 — effectively inert or boundary-sensitive factors

The complete factor and paired-contrast CSV files should be used to identify small effects. Any apparent invariance is a property of this bounded configuration, seed set, and stock/surrogate model, not a general technology statement. The LiFi physical state is sensitive to FOV through the explicit FOV gate; its packet-access abstraction and uncalibrated parameters remain important limitations.

## Generated analysis artifacts

- `run_level_kpi.csv`
- `factor_main_effect_summary.csv`
- `paired_factor_contrasts.csv`
- `branch_variation_summary.csv`
- `lifi_physical_grouped_summary_recomputed.csv`
- `lifi_fov_paired_physical_contrasts.csv`
- `throughput_vs_offered_load.svg`
- `delay_vs_offered_load.svg`
- `lifi_fov_physical_response.svg`

No new ns-3 simulation was run by this analysis script.
