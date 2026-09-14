# Final synthetic three-RAT wireless dataset

This directory contains the final W4C synthetic wireless dataset used in the
manuscript. It is a generated simulation dataset, not a measurement from the
practical wireless testbed.

This is the release corresponding to the final three-RAT wireless results in
the manuscript. The separate upstream framework repository's `NS3_Wireless/`
directory is an earlier LTE/EPC, IEEE 802.11n, and CSMA-surrogate baseline; it
is not the source of the W4C results.

The scenarios were executed with ns-3.44 and CTTC 5G-LENA `5g-lena-v4.0.y`
for the 5G NR branch, native ns-3 IEEE 802.11ax for the Wi-Fi branch, and an
equation-driven line-of-sight LiFi/OWC model. The LiFi model includes the
Lambertian LOS gain, receiver field-of-view gate, received optical power,
photodetector responsivity, shot and thermal noise, electrical SNR, BER, and
packet-error probability. It uses a stock packet-access abstraction and is
uncalibrated to the practical testbed; it is not a complete standardized LiFi
PHY/MAC.

## Dataset scope

The frozen sweep contains 48 configurations:

- offered load: 2, 5, 10, and 20 Mbps per application flow;
- mobility speed: 0.5 and 3 m/s;
- LiFi receiver FOV: 40 and 70 degrees;
- random seed: 1, 2, and 3;
- simulation duration: 10 s;
- packet size: 1,024 bytes.

Each configuration contains three NR, three Wi-Fi 802.11ax, and three LiFi
application flows. The final application table therefore contains 432 rows:
144 NR, 144 Wi-Fi 802.11ax, and 144 LiFi. The raw FlowMonitor exports contain
624 flow rows in total, including non-application/control flows that are
excluded from the final application table.

## Principal files

- `analysis/final_application_flow_dataset.csv` is the final per-flow table.
- `analysis/run_level_kpi.csv` contains run-level summaries after averaging
  the three CPE flows within each branch.
- `analysis/lifi_physical_summary.csv` contains per-CPE summaries of sampled
  LiFi optical states.
- `analysis/sweep_structure_summary.json` and
  `analysis/sweep_structure_report.md` record the structural checks.
- `analysis/scientific_sweep_analysis.md` records the bounded factor analysis.
- `runs/` contains the per-configuration FlowMonitor XML, KPI tables, optical
  state tables, scenario metadata, flow mappings, and run logs.
- `ns3/`, `config/`, `run_w4c_sweep.py`, `aggregate_w4c.py`, and
  `analyze_w4c.py` contain the project-local source, configuration, and
  aggregation/analysis scripts.
- `lifi_validation/` contains the independent mathematical reference and
  LiFi equation checks.
- `W4C_FINAL_SWEEP_REPORT.md` provides the validation and claim boundaries.

The column definitions and units are given in `data_dictionary.csv`. The
FlowMonitor `lostPackets` value is retained as a FlowMonitor-reported field;
it is not reinterpreted as terminal packet loss at the simulation stopping
time.

The synthetic dataset uses the same technology classes as the practical
multi-access testbed, but it is a separate, uncalibrated simulation artifact.
The release does not imply numerical reproduction of the measured telemetry.
The dataset, metadata, and associated documentation are licensed under
[CC BY-NC 4.0](../LICENSE), permitting sharing and adaptation with
attribution for non-commercial purposes. Software and identified third-party
material retain their own terms.
