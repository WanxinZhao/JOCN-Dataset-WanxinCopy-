# Independent validation of the synthetic ns-3 wireless dataset

This directory contains the independent validation evidence used for the
synthetic wireless experiment reported in the manuscript. The released
experiment comprises 48 ns-3 configurations, 624 raw FlowMonitor records, and
432 explicitly mapped application-flow records. The simulated access branches
are LTE/EPC, Wi-Fi 802.11n, and a CSMA-based LiFi surrogate.

The validation addresses implementation and data-extraction correctness under
the declared simulation assumptions. It does not establish physical-testbed
calibration, a physical LiFi channel model, or a universal ranking among
access technologies. The corresponding simulator source and archived dataset
are released in the cited workflow repository; this directory records the
independent checks applied to those artefacts.

## Evidence structure

- `validation_report.md`: complete methods, results, interpretation limits,
  and execution environment for the validation.
- `archive_audit.py`: independent parser and consistency checks for the
  archived scenario, FlowMonitor, KPI, and aggregate records.
- `flowmonitor_recomputed.csv`, `kpi_recomputation_comparison.csv`, and
  `kpi_recomputation_summary.json`: archive-wide independent KPI
  reconstruction and numerical comparison.
- `sweep_consistency.csv` and `sweep_consistency_summary.json`: checks of the
  48 configurations and 432 application-flow mappings.
- `grouped_kpi_summary.csv`, `sweep_sanity_report.md`, and
  `sweep_sanity_summary.json`: bounded descriptive checks of the parameter
  sweep.
- `replay_results.csv`, `replay_report.md`, and `replays/`: source,
  configuration, logs, and fresh outputs for the three representative
  replays. Compiled binaries are intentionally omitted.
- `repeatability.csv` and `seed_sensitivity.csv`: fixed-seed repeatability and
  three-seed descriptive summaries.
- `independent_reference/`: separately written stock-ns-3 reference source,
  comparison outputs, and build/run logs. The compiled binary is intentionally
  omitted.
- `ns3_claim_boundary.md`: terminology and interpretation boundary used in
  the manuscript.

## Principal validation results

- All 432 application-flow packet counters and FlowMonitor lost-packet fields
  matched the archived KPI exports exactly.
- Maximum absolute reconstruction differences were
  `5.57e-5 Mbps` for throughput, `3.16e-3 ms` for mean delay, and
  `1.10e-5 ms` for mean jitter; these differences arise from XML time
  serialisation precision.
- Three representative configurations rebuilt and replayed with nine
  application flows each and zero KPI delta.
- Two executions of the fixed-seed representative configuration produced
  identical application-flow KPIs.
- The independent reference passed five topology/configuration checks and all
  63 keyed KPI comparisons.

FlowMonitor `lostPackets/txPackets` is retained as a simulator-reported loss
ratio. It is not interpreted as terminal packet loss at the finite simulation
stop.
