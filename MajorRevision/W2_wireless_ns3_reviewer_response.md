# Wireless synthetic-data revision response

## Reviewer 3, Comment 4 — Independent correctness and reproducibility validation

We agree that a successful simulator build and run alone cannot detect a plausible but incorrectly configured scenario, KPI extractor, or flow mapping. In response, we replaced the former synthetic wireless result path with a bounded three-RAT W4C experiment using ns-3.44, CTTC 5G-LENA `5g-lena-v4.0.y` for 5G NR, native IEEE 802.11ax for Wi-Fi 6, and an equation-driven LOS LiFi/OWC link model. The previous LTE/EPC + 802.11n + CSMA-surrogate implementation is retained only as an explicitly labelled legacy/development baseline and is not used as the final synthetic result.

The final wireless evidence is:

1. **Backend and equation qualification.** The 5G-LENA NR and native 802.11ax branches build and execute in the qualified ns-3.44 environment. The independent LiFi mathematical test suite passes 9/9 equation-behaviour tests. A compiled ns-3 LiFi link probe agrees with the independent Python reference for 15/15 compared values across aligned-near, aligned-far, and out-of-FOV geometries.
2. **Integrated flow and interface mapping.** A final-source integrated acceptance run contains three NR, three Wi-Fi 802.11ax, and three LiFi application flows. All 9/9 declared five-tuple mappings resolve to the expected branch/CPE/interface.
3. **Fixed-seed repeatability.** Two executions of the same final-source configuration with the same ns-3.44 build, seed, run number, workload, mobility, and FOV produce byte-identical run configuration, scenario metadata, flow mapping, KPI, FlowMonitor XML, and optical-state outputs.
4. **Full bounded sweep.** The final grid contains 4 offered loads (2/5/10/20 Mbps), 2 mobility speeds (0.5/3 m/s), 2 LiFi receiver FOVs (40/70 degrees), and 3 seeds, giving 48 configurations. All 48 completed. Each contains 9 application flows, yielding 432 application-flow records; all 432 mappings pass. The raw FlowMonitor exports contain 624 rows because they also include non-application/control flows, which are excluded from the application table.

These tests substantially strengthen confidence that the final synthetic dataset is reproducible and internally consistent with the declared ns-3 scenario and KPI/export pipeline. They do not establish physical-testbed calibration, universal RAT rankings, or physical-model fidelity. The LiFi model is an equation-driven LOS OWC/error abstraction behind a stock packet-access path, not a complete standardized LiFi PHY/MAC.

The FlowMonitor field is reported as the **FlowMonitor-reported packet-loss ratio**, `lostPackets/txPackets`. It is not interpreted as terminal packet loss at the finite simulation stopping time; in the W4C application table, 172/432 rows have `tx_packets-rx_packets` different from the FlowMonitor `lostPackets` field.

Evidence: the public synthetic-data repository contains the complete release at `NS3_Wireless_W4C_ThreeRAT/`, including the source, preflight, 48 run directories, aggregate tables, independent LiFi tests, and final-source repeatability outputs. The release summary is `NS3_Wireless_W4C_ThreeRAT/W4C_FINAL_SWEEP_REPORT.md`.

## Reviewer 3, Comment 3 — Simulation-side evaluation of the LLM workflow

For the simulation-side part of this comment, the revised experiment evaluates more than one demonstration point. The LLM-driven workflow constructs and executes a heterogeneous synthetic scenario containing 5G NR, Wi-Fi 802.11ax, and an equation-driven LOS LiFi/OWC model, and produces a bounded 48-configuration dataset with 432 explicitly mapped application-flow records. The analysis averages the three CPE flows within each run and retains the three seeds as the replicate axis for factor summaries.

The new evidence supports executable scenario construction, technology-class coverage, configuration coverage, deterministic repeatability under a fixed build/seed, independent LiFi equation checking, integrated branch/interface mapping, and full-sweep structural completion. It does not establish an LLM advantage over deterministic scripts and does not recover unavailable historical LLM token counts, API cost, latency, prompts, provider metadata, or model-version logs. No such historical quantities are inferred from the simulator outputs.

The practical measured wireless dataset remains separate from the synthetic ns-3 dataset. Sharing the three technology classes does not imply that the synthetic outputs reproduce measured values.

## Reviewer 3, Comment 10 — ns-3 terminology and model boundaries

The final synthetic backend is now described consistently as:

- **5G NR using CTTC 5G-LENA `5g-lena-v4.0.y` on ns-3.44**;
- **Wi-Fi 6 / IEEE 802.11ax using native ns-3 APIs**;
- **an equation-driven LOS LiFi/OWC model** with an explicitly documented stock packet-access abstraction.

The final W4C experiment is not described as LTE/EPC, 802.11n, or a CSMA-only LiFi surrogate. Those terms refer only to the preserved legacy baseline when it is mentioned. The manuscript also states that the LiFi model does not provide a complete standardized LiFi PHY/MAC or calibrated optical-testbed emulation, and that cross-branch KPI differences are configuration-specific rather than universal technology rankings.

## Reviewer 1 — Synthetic wireless dataset summary

The dataset-summary table now separates the practical measured wireless campaign from the generated synthetic wireless DT dataset. The synthetic entry identifies ns-3.44 and CTTC 5G-LENA, native 802.11ax, equation-driven LOS LiFi/OWC, 48 configurations, 432 application-flow records, 624 raw FlowMonitor records, the three seeds, the four-by-two-by-two-by-three sweep, and the validation artifacts. No unsupported synthetic file-size or licence assertion is added.

## Evidence locations and claim boundary

The final manuscript locations are `sec:ns3_wireless`, `tab:dataset_summary`, `tab:ns3_validation`, `fig:w4c_throughput`, and `fig:w4c_lifi_fov`. The final synthetic application table is `NS3_Wireless_W4C_ThreeRAT/analysis/final_application_flow_dataset.csv`; the structure summary is `NS3_Wireless_W4C_ThreeRAT/analysis/sweep_structure_summary.json`; the run-aware factor analysis is `NS3_Wireless_W4C_ThreeRAT/analysis/scientific_sweep_analysis.md`.

The added evidence supports the claim that the workflow generated a bounded, reproducible, internally checked synthetic three-RAT dataset under declared ns-3 and optical-model assumptions. It does not support calibrated reproduction of the practical 5G NR/Wi-Fi 6/LiFi testbed, a complete physical LiFi simulator, a terminal-loss interpretation of the FlowMonitor field, or a universal superiority claim for any RAT.
