# Sweep sanity report

This report uses the existing 432 application-flow rows in /home/ubuntu/Desktop/LLM Driven wireless environment generation/LLM-Driven-Multi-Agent-Optical-Digital-Twin-for-Automated-Data-Generation/NS3_Wireless_Hybrid_ParamSweep/scenarios.csv. It is an empirical sanity analysis, not a proof of universal technology behaviour.

## Coverage

- application rows: 432
- access counts: {'LTE/EPC': 144, 'Wi-Fi': 144, 'LiFi-surrogate': 144}
- offered loads: [2.0, 5.0, 10.0, 20.0]
- mobility speeds: [0.5, 3.0]
- LiFi rates: [50.0, 100.0]
- seeds: [1, 2, 3]

## Invariant or surprising behavior

- access_diversity_score is invariant in scenarios.csv: 0.75 across 432 rows.

## Interpretation boundary

- The low-load rows are approximately load-limited at the application-flow level.
- High offered load should be described through the observed grouped means; no strict monotonicity is assumed.
- Mobility differences are empirical deltas of this finite configuration, not a general mobility law.
- LiFi-rate changes are relevant to the CSMA surrogate branch configuration; they do not validate a physical optical LiFi channel.
- The uploaded packet_loss_ratio uses FlowMonitor lostPackets and is nonzero in some high-load Wi-Fi/LiFi-surrogate rows; it must not be presented as the complete terminal tx-rx loss because tx-rx gaps remain in every application flow.
- access_diversity_score is a fixed postprocessing constant in the uploaded dataset, so it cannot support an independent access-diversity effect analysis.

## Parameter contrasts

The complete paired contrasts are available in grouped_kpi_summary.csv and in the JSON summary. They are reported as differences, not as universal rankings.

## Evidence location

- grouped results: /home/ubuntu/Desktop/LLM Driven wireless environment generation/W1_NS3_VALIDATION/grouped_kpi_summary.csv
- source table: /home/ubuntu/Desktop/LLM Driven wireless environment generation/LLM-Driven-Multi-Agent-Optical-Digital-Twin-for-Automated-Data-Generation/NS3_Wireless_Hybrid_ParamSweep/scenarios.csv
- semantic postprocessing implementation: /home/ubuntu/Desktop/LLM Driven wireless environment generation/src/llm_ns3/data_upload.py:364-405
