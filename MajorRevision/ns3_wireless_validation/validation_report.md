# WIRELESS_REVISION_W1_NS3_VALIDATION

W1 validation scope: only the archived synthetic wireless ns-3 dataset and its simulation evidence. Optical data, semantic-fusion experiments, manuscript text, commits, pushes, and large new simulations were not modified or run.

## Evidence labels

- **OBSERVED**: directly read from code, archive artifacts, output files, logs, or the W1 validation outputs.
- **INFERRED**: interpretation derived from an observed implementation or result, without an explicit source statement.
- **MISSING**: not recoverable from the inspected wireless artifacts.

## 1. Executive verdict

**PASS_WITH_LIMITATIONS**.

**OBSERVED:** all 48 archived configurations are present and marked completed; the archive contains 624 raw FlowMonitor rows and 432 application-flow rows. An independent XML parser reconstructs all rows. Application packet counters and FlowMonitor lost-packet counts match the archived `kpi.csv` exactly; application throughput, delay, and jitter agree within XML serialization precision. All three representative archived sources were rebuilt with the available ns-3.44 libraries, executed, and produced nine application flows with zero numerical deltas against their archived FlowMonitor results. The medium configuration is deterministic under two same-seed repeats. A separate hand-written ns-3.44 reference produces the same nine classifier-keyed application flows and all 63 compared values.

**LIMITATION:** FlowMonitor `lostPackets` is not terminal `txPackets-rxPackets` at the exact 10 s stop. The current `packet_loss_ratio` is therefore a FlowMonitor loss ratio, not a complete end-to-end terminal loss ratio. The expanded `scenario.json` retains base metadata values for traffic rate, mobility speed, and sometimes LiFi rate while the actual sweep values are carried in `expansion_parameters` and passed by CLI. These are claim/metadata limitations, not evidence of a corrupted simulation binary.

**INFERRED:** the current 48-run dataset is usable for a bounded, configuration-specific feasibility result if the revision explicitly labels it synthetic, uses LTE/EPC and CSMA-based LiFi-surrogate terminology, reports the FlowMonitor loss definition, and does not infer physical LiFi or universal technology rankings.

## 2. ns-3 execution environment

| Item | Observed value | Evidence |
| --- | --- | --- |
| Version | 3.44 | /home/ubuntu/Desktop/ns-allinone-3.44/ns-3.44/VERSION:1 |
| Source/build root | /home/ubuntu/Desktop/ns-allinone-3.44/ns-3.44 | /home/ubuntu/Desktop/ns-allinone-3.44/ns-3.44/build |
| Build profile | default; Unix Makefiles; CMake `CMAKE_BUILD_TYPE=default` | /home/ubuntu/Desktop/ns-allinone-3.44/ns-3.44/build/CMakeCache.txt:30,714 |
| Compiler | /usr/bin/c++ GNU 15.2.0 (Ubuntu 15.2.0-16ubuntu1) | `/usr/bin/c++ --version` |
| Validation compile flags | C++20, -Os, -g, -DNDEBUG, ns-3 build includes, libxml2 | /home/ubuntu/Desktop/ns-allinone-3.44/ns-3.44/build/scratch/CMakeFiles/scratch_llm_ns3_20260511T163516Z_indoor_hybrid.dir/flags.make:5-10 |
| Archive | /home/ubuntu/Desktop/LLM Driven wireless environment generation/LLM-Driven-Multi-Agent-Optical-Digital-Twin-for-Automated-Data-Generation/NS3_Wireless_Hybrid_ParamSweep/artifacts.zip | SHA-256 f21bb0e9597ee80d794605f891dac14e35795578162bb235fb80408a88c2170f |
| Archive source diversity | one byte-identical generated.cc SHA-256 across all 48 roots | SHA-256 ffdd41b53b70e36f5cdea1d8abf82f57b0856a8b5ce4182ecf3f1568970be16d |

The archived expansion wrapper uses the ns-3 launcher and passes the six scenario parameters at `/home/ubuntu/Desktop/LLM Driven wireless environment generation/src/llm_ns3/data_expand.py:_run_ns3_variant`, lines 150-205, especially lines 184-190. For W1, the exact archived sources were copied to `W1_NS3_VALIDATION/replays/`, compiled directly with `/usr/bin/c++`, and executed against the existing build libraries. This avoids rebuilding Python bindings and does not modify the ns-3 source/build tree. The exact commands are in `W1_NS3_VALIDATION/replays/*/compile.log` and `run.log`.

## 3. Full 48-run FlowMonitor KPI recomputation

**OBSERVED:** `W1_NS3_VALIDATION/archive_audit.py:parse_flowmon` parses FlowMonitor XML independently of `/home/ubuntu/Desktop/LLM Driven wireless environment generation/src/llm_ns3/data_upload.py`. The parser derives the application mapping from XML classifier addresses and UDP destination port 9, then applies the KPI equations used by the archived generated source at `W1_NS3_VALIDATION/replays/medium_load_high_mobility/archived_generated.cc:L215-L222`:

- `duration = timeLastRxPacket - timeFirstTxPacket`; if non-positive, use `simTime - 1` for a 10 s run.
- `throughput_mbps = rxBytes * 8 / duration / 1e6`.
- `mean_delay_ms = delaySum_seconds * 1000 / rxPackets` when `rxPackets > 0`.
- `mean_jitter_ms = jitterSum_seconds * 1000 / (rxPackets - 1)` when `rxPackets > 1`.

| Metric | Compared application rows | Exact matches | Within audit tolerance | Max absolute error | Mean absolute error | Max relative error |
| --- | --- | --- | --- | --- | --- | --- |
| tx_packets | 432 | 432 | 432 | 0 | 0 | 0 |
| rx_packets | 432 | 432 | 432 | 0 | 0 | 0 |
| lost_packets | 432 | 432 | 432 | 0 | 0 | 0 |
| throughput_mbps | 432 | 0 | 432 | 5.56977e-05 | 1.05892e-05 | 5.00203e-06 |
| mean_delay_ms | 432 | 0 | 382 | 0.00316445 | 0.00012188 | 5.66196e-06 |
| mean_jitter_ms | 432 | 0 | 432 | 1.10013e-05 | 1.31925e-06 | 6.31775e-06 |

For completeness, the same independent comparison over all 624 rows (including four infrastructure/control flows per run) is:

| Metric | Compared all rows | Exact matches | Within audit tolerance | Max absolute error | Mean absolute error | Max relative error |
| --- | --- | --- | --- | --- | --- | --- |
| tx_packets | 624 | 624 | 624 | 0 | 0 | 0 |
| rx_packets | 624 | 624 | 624 | 0 | 0 | 0 |
| lost_packets | 624 | 624 | 624 | 0 | 0 | 0 |
| throughput_mbps | 624 | 0 | 432 | 2555 | 228.409 | 0.28 |
| mean_delay_ms | 624 | 96 | 574 | 0.00316445 | 8.43782e-05 | 5.66196e-06 |
| mean_jitter_ms | 624 | 192 | 624 | 1.10013e-05 | 9.13324e-07 | 6.31775e-06 |

The application audit tolerances are 1e-6 for packet counters and 1e-4 in the reported metric units for continuous metrics. The maximum application differences are 5.57e-5 Mbps throughput, 3.16e-3 ms delay, and 1.10e-5 ms jitter; their relative errors are at most approximately 6.32e-6. The larger all-flow throughput discrepancy (maximum 2555 Mbps) occurs only in short infrastructure/control flows whose XML times are rounded at a scale comparable to their sub-microsecond duration; those four flow IDs are not exported as application rows. The all-flow comparison is retained in `kpi_recomputation_summary.json` rather than hidden.

**OBSERVED physical checks:** zero negative recomputed values, zero nonfinite recomputed values, and zero archived FlowMonitor loss ratios outside [0,1]. The evidence files are `flowmonitor_recomputed.csv`, `kpi_recomputation_comparison.csv`, and `kpi_recomputation_summary.json`.

### Packet accounting

| Branch | Application rows | Σ(tx-rx) | Σ FlowMonitor lostPackets | Σ(tx-rx-lostPackets) |
| --- | --- | --- | --- | --- |
| LTE/EPC | 144 | 738084 | 0 | 738084 |
| Wi-Fi | 144 | 107458 | 51032 | 56426 |
| LiFi-surrogate | 144 | 84294 | 36282 | 48012 |

**OBSERVED:** `tx_packets-rx_packets` is nonzero in 432/432 application flows, while FlowMonitor `lostPackets` is nonzero in 54/432. The relation `lost_packets == tx_packets-rx_packets` therefore does not hold for the archived application flows.

**OBSERVED explanation from the installed ns-3 source:** `FlowMonitor::MaxPerHopDelay` defaults to 10 s at `/home/ubuntu/Desktop/ns-allinone-3.44/ns-3.44/src/flow-monitor/model/flow-monitor.cc:L36-L42`; `CheckForLostPackets(Time)` increments `lostPackets` only for still-tracked packets whose age reaches that delay at `L320-L341`; explicit probe drops also increment it at `L274-L310`. The generated program stops at exactly 10 s (`archived_generated.cc:L203`) and serializes at that time (`flow-monitor.cc:L431-L453`). Thus packets still in flight or not yet beyond the timeout can contribute to `tx-rx` without appearing in `lostPackets`.

**Claim boundary:** the archived field is correctly extracted as the FlowMonitor-reported loss count, but the column name/interpretation must be qualified as `FlowMonitor loss ratio`; it is not evidence of zero terminal packet loss.

## 4. End-to-end sweep consistency

**OBSERVED:** the archive has 48 unique full scenario keys and each root has 13 FlowMonitor rows, nine XML-classifier-identified application rows, and 13 `kpi.csv` rows. `sweep_consistency.csv` contains 432 expected application keys; all 432 are present exactly once in `scenarios.csv`; no missing/extra configurations, duplicate full run keys, duplicate application keys, flow ID mismatches, access mapping mismatches, CPE mismatches, or KPI mismatches were found.

| Check | Expected | Observed |
| --- | --- | --- |
| Expected run configurations | 48 | 48 |
| Expected raw FlowMonitor/KPI rows | 624 | 624 |
| Expected application rows | 432 | 432 |
| Application FlowMonitor IDs | 5-13 | 5-13 in every root |
| Structural issue rows | 0 | 0 |
| Archive status | completed | 48/48 status.json files |

The independent XML classifier mapping is: IDs 5-7 LTE/EPC CPE1-CPE3, IDs 8-10 Wi-Fi CPE1-CPE3, and IDs 11-13 LiFi-surrogate CPE1-CPE3. This agrees with the export mapping in `/home/ubuntu/Desktop/LLM Driven wireless environment generation/src/llm_ns3/data_upload.py:_flow_access_map`, lines 255-273, but W1 did not use that function as its primary mapping source.

### Parameter provenance nuance

**OBSERVED:** `/home/ubuntu/Desktop/LLM Driven wireless environment generation/src/llm_ns3/data_expand.py:_create_variant_run`, lines 131-146, writes the sweep values to `scenario.expansion_parameters`; `_run_ns3_variant`, lines 184-190, passes them on the command line. `/home/ubuntu/Desktop/LLM Driven wireless environment generation/src/llm_ns3/data_upload.py:_ns3_config`, lines 299-320, records those CLI values in `ns3_config_json`. The actual 48 status records and 432 exported rows therefore carry the intended expansion values.

**OBSERVED limitation:** the base scenario fields were not rewritten for every expanded variant. Across the 48 roots: `scenario.traffic.data_rate` disagrees with expansion in 36, `scenario.mobility.speed_mps` in 48, and `scenario.lifi.data_rate` in 24. All 48 archived sources retain the same defaults (`simTime=10`, `seed=1`, `offeredLoadMbps=10`, `packetSize=1024`, `mobilitySpeed=1.5`, `lifiRateMbps=100`); source-default mismatches against the intended CLI parameters are seed 32, offered load 36, mobility 48, LiFi rate 24, with no mismatch for duration or packet size. Running a source without the recorded CLI overrides would not reproduce its expanded scenario. W1 replays used the recorded CLI parameters.

This is a reproducibility/metadata issue to correct in the released manifest or export logic; it did not create a structural mismatch in the archived executed outputs because the actual commands are recorded in `ns3_config_json` and `status.json`.

## 5. Scientific sweep sanity analysis

The grouped file has 48 groups (three branches × four loads × two mobility speeds × two LiFi rates), nine application rows per group, three seeds, and three CPEs. The following table averages equally over the relevant seeds, CPEs, mobility values, and LiFi rates; it is descriptive, not a universal technology ranking.

| Access branch | Offered load (Mbps) | Throughput (Mbps) | FlowMonitor loss ratio | Delay (ms) | Jitter (ms) |
| --- | --- | --- | --- | --- | --- |
| LTE/EPC | 2 | 2.0542 | 0 | 6.51244 | 0.182099 |
| LTE/EPC | 5 | 5.13433 | 0 | 6.51827 | 1.48725 |
| LTE/EPC | 10 | 5.82795 | 0 | 18.1516 | 1.74201 |
| LTE/EPC | 20 | 5.82795 | 0 | 18.5897 | 1.85438 |
| Wi-Fi | 2 | 2.05492 | 0 | 2.58793 | 0.102103 |
| Wi-Fi | 5 | 5.13418 | 0 | 2.58197 | 0.0818996 |
| Wi-Fi | 10 | 10.1397 | 0 | 2.97776 | 0.531208 |
| Wi-Fi | 20 | 17.9071 | 0.0645135 | 362.954 | 0.601115 |
| LiFi-surrogate | 2 | 2.05511 | 0 | 2.26881 | 0.0016217 |
| LiFi-surrogate | 5 | 5.13568 | 0 | 2.26806 | 0.000661502 |
| LiFi-surrogate | 10 | 10.2693 | 0 | 2.2675 | 0.000335988 |
| LiFi-surrogate | 20 | 18.3668 | 0.0458669 | 340.814 | 0.120207 |

**OBSERVED:** low-load application throughput is approximately offered-load limited. At 10 and 20 Mbps, LTE/EPC saturates near 5.83 Mbps in this configuration, while Wi-Fi and the LiFi surrogate show high-load delay/loss changes. The exact 48-group values, standard deviations, seed counts, and CPE counts are in `grouped_kpi_summary.csv`.

**OBSERVED parameter contrasts:** LiFi-rate changes are exactly invariant for LTE/EPC and Wi-Fi in the grouped results, as expected from branch separation. For the LiFi surrogate, the 50-to-100 Mbps difference is negligible at 2-10 Mbps but at 20 Mbps is approximately +4.339 Mbps throughput, -677.266 ms delay, and -0.240 ms jitter. Mobility changes are exactly invariant for LTE/EPC and LiFi-surrogate in the grouped output; for Wi-Fi the high-load 3.0-minus-0.5 m/s contrast is approximately -0.592 Mbps throughput and +81.15 ms delay. These are empirical properties of this finite model, not physical laws.

**OBSERVED postprocessing behaviour:** `access_diversity_score` is exactly 0.75 for all 432 rows because `/home/ubuntu/Desktop/LLM Driven wireless environment generation/src/llm_ns3/data_upload.py:_semantic_features`, lines 380-383, assigns a constant per branch. It cannot support a simulated access-diversity effect. `congestion_risk` counts are low 306, medium 84, high 42. The code at lines 376-390 uses fixed thresholds rather than a learned label model: high is `queueing_risk_score >= 0.6` or `packet_loss_ratio >= 0.05`; medium is `queueing_risk_score >= 0.2` or throughput efficiency `< 0.8`; otherwise low. All 42 high rows meet both high conditions; 72 medium rows are triggered by efficiency and 12 by queueing risk. Labels are therefore deterministic thresholded postprocessing, not independent ground truth.

**OBSERVED/inferred realism boundary:** LiFi-surrogate jitter is sub-microsecond in much of the low/medium-load output but rises at high load. The observed low jitter is consistent with the CSMA/10 ns surrogate; it should not be interpreted as a physical optical LiFi result. The Yans Wi-Fi branch and stock LTE/EPC branch have no custom calibrated cross-technology error model in the archived source, so cross-branch differences are configuration-specific.

## 6. Representative replay results

| Configuration | Archive run | Compile rc | Run rc | App flows | Max abs throughput delta | Max abs loss delta | Max abs delay delta | Max abs jitter delta |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| high_load_high_mobility | 20260619T104709Z-hybrid-seed3-t10p0-l20p0-s3p0 | 0 | 0 | 9 | 0 | 0 | 0 | 0 |
| low_load_low_mobility | 20260619T103518Z-hybrid-seed1-t10p0-l2p0-s0p5 | 0 | 0 | 9 | 0 | 0 | 0 | 0 |
| medium_load_high_mobility | 20260619T104328Z-hybrid-seed2-t10p0-l10p0-s3p0 | 0 | 0 | 9 | 0 | 0 | 0 | 0 |

**OBSERVED:** low-load/low-mobility (2 Mbps, 0.5 m/s, 50 Mbps, seed 1), medium (10 Mbps, 3 m/s, 100 Mbps, seed 2), and high-load/high-mobility (20 Mbps, 3 m/s, 100 Mbps, seed 3) were all rebuilt and executed. Each produced nine application flows. All packet counters and all four independently parsed KPI deltas are zero. This is stronger than a build-only check, but it is still a three-configuration replay rather than a fresh rerun of all 48 configurations.

Evidence: `W1_NS3_VALIDATION/replay_results.csv`, `replay_report.md`, and `replays/{low_load_low_mobility,medium_load_high_mobility,high_load_high_mobility}/`.

## 7. Same-seed repeatability

The medium configuration `20260619T104328Z-hybrid-seed2-t10p0-l10p0-s3p0` was executed twice with the same rebuilt source, ns-3.44 libraries, seed 2, parameters, and command structure. **OBSERVED:** both runs returned 0, both produced nine application flows, all four KPI exact-match counts are 9/9, and maximum absolute differences are throughput 0, loss 0, delay 0, and jitter 0. The implementation is deterministic for this fixed build and configuration.

This does not establish bitwise reproducibility across a different compiler, ns-3 build, operating system, or unrecorded run number. The generated source calls `RngSeedManager::SetSeed(seed)` at `archived_generated.cc:L37` and does not call `RngSeedManager::SetRun`; the archive uses seeds 1, 2, and 3 as separate configurations.

## 8. Three-seed sensitivity

The fixed configuration is offered load 10 Mbps, mobility 3 m/s, LiFi-surrogate rate 100 Mbps, packet size 1024, and duration 10 s. Values below use the FlowMonitor loss definition and aggregate the nine application flows (three CPEs × seeds 1-3). `all-flow mean ± SD` is across those nine flow values; seed columns are per-seed CPE means and `seed-mean SD` is the SD across the three seed means.

| Access | Metric | n | All-flow mean | All-flow SD | Seed 1 | Seed 2 | Seed 3 | Seed-mean SD |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| LTE/EPC | throughput_mbps | 9 | 5.82795 | 0.000529773 | 5.82795 | 5.82795 | 5.82795 | 0 |
| LTE/EPC | packet_loss_ratio | 9 | 0 | 0 | 0 | 0 | 0 | 0 |
| LTE/EPC | mean_delay_ms | 9 | 18.1516 | 0.00683811 | 18.1515 | 18.1515 | 18.1518 | 0.000153932 |
| LTE/EPC | mean_jitter_ms | 9 | 1.74201 | 0.000496893 | 1.74195 | 1.74212 | 1.74195 | 0.00010189 |
| Wi-Fi | throughput_mbps | 9 | 10.1396 | 0.379109 | 10.2645 | 10.266 | 9.88835 | 0.217592 |
| Wi-Fi | packet_loss_ratio | 9 | 0 | 0 | 0 | 0 | 0 | 0 |
| Wi-Fi | mean_delay_ms | 9 | 3.00716 | 0.176693 | 2.97267 | 2.83717 | 3.21165 | 0.189608 |
| Wi-Fi | mean_jitter_ms | 9 | 0.546808 | 0.188 | 0.543469 | 0.456369 | 0.640586 | 0.092154 |
| LiFi-surrogate | throughput_mbps | 9 | 10.2694 | 0.00313947 | 10.2703 | 10.2706 | 10.2672 | 0.00189613 |
| LiFi-surrogate | packet_loss_ratio | 9 | 0 | 0 | 0 | 0 | 0 | 0 |
| LiFi-surrogate | mean_delay_ms | 9 | 2.18139 | 0.0749253 | 2.18115 | 2.18109 | 2.18194 | 0.000469685 |
| LiFi-surrogate | mean_jitter_ms | 9 | 0.000321168 | 0.000305615 | 0.00024637 | 0.000213418 | 0.000503716 | 0.000158947 |

**OBSERVED:** seed sensitivity is very small for LTE/EPC and the LiFi surrogate at this fixed point, while Wi-Fi shows larger seed variation (throughput seed means approximately 10.264, 10.266, and 9.888 Mbps). This is why the revision should retain mean/SD or confidence intervals and avoid presenting one run as a universal branch ranking.

Evidence: `W1_NS3_VALIDATION/repeatability.csv` and `seed_sensitivity.csv`.

## 9. Independent hand-written ns-3 baseline

**OBSERVED:** `W1_NS3_VALIDATION/independent_reference/reference.cc` is a new fixed-configuration C++ program, written separately from the archived generated source. It manually instantiates three CPEs, Wi-Fi 802.11n, LTE/EPC, the CSMA-based LiFi surrogate, the same 10 Mbps/1024-byte/10 s/3 m/s/100 Mbps/seed-2 operating point, and nine downlink UDP flows. It uses FlowMonitor and emits its own XML and manifest.

| Metric | Records | CONSISTENT | MATERIALLY_DIFFERENT | Max absolute delta |
| --- | --- | --- | --- | --- |
| flowmonitor_lost_packets | 9 | 9 | 0 | 0 |
| mean_delay_ms | 9 | 9 | 0 | 0 |
| mean_jitter_ms | 9 | 9 | 0 | 0 |
| packet_loss_ratio | 9 | 9 | 0 | 0 |
| rx_packets | 9 | 9 | 0 | 0 |
| throughput_mbps | 9 | 9 | 0 | 0 |
| tx_packets | 9 | 9 | 0 | 0 |

**OBSERVED:** generated and reference XML each have 9 application flows; all expected flows are present. All 63 keyed metric comparisons are CONSISTENT, including exact equality for packet counters and FlowMonitor loss, and zero numerical delta for throughput, delay, and jitter. The independent topology/configuration checks are 5/5 CONSISTENT (flow count, access/CPE keys, destination addresses/ports, three CPEs per branch, and mapping correspondence). The comparison key is XML classifier-derived access branch and CPE rather than numeric flow ID. Continuous KPI tolerance is max(1e-6, 1% of the generated value); counter/loss tolerance is exact.

**INFERRED:** this independently validates the declared topology/access mapping and the archived KPI behaviour under the same stock ns-3.44 assumptions. It does not validate physical realism, LiFi optical physics, or the LLM’s historical generation quality.

Evidence: `W1_NS3_VALIDATION/independent_reference/reference.cc`, `comparison.csv`, `topology_config_comparison.csv`, `report.md`, `compile.log`, `run.log`.

## 10. Model and terminology lock

The source-level evidence is:

- **LTE/EPC:** `LteHelper` + `PointToPointEpcHelper` at archived source lines 141-152. The schema explicitly states that 5G NR is unsupported at `/home/ubuntu/Desktop/LLM Driven wireless environment generation/src/llm_ns3/schema.py:125-129`.
- **Wi-Fi 802.11n:** `WIFI_STANDARD_80211n`, `YansWifiChannelHelper::Default`, and `YansWifiPhyHelper` at lines 112-124. The scenario metadata says 20 MHz, but the generated source does not explicitly set a channel-width attribute; the revision should not present 20 MHz as independently validated by the source unless this is clarified.
- **CSMA-based LiFi surrogate:** `CsmaHelper`, swept 50/100 Mbps, and 10 ns delay at lines 130-139. No optical LOS/FOV, photodiode, optical modulation, shot-noise, blockage, or calibrated optical error model is present in this branch.

The locked wording and unsupported claims are in `W1_NS3_VALIDATION/ns3_claim_boundary.md`.

## 11. Reviewer-ready evidence

| Reviewer concern | Experiment performed | Evidence | Result | Claim now supported | Remaining limitation |
| --- | --- | --- | --- | --- | --- |
| R3-4: generated data lack independent correctness validation | Independent FlowMonitor XML recomputation for all 48; three source replays; same-seed repeat; hand-written reference | `kpi_recomputation_summary.json`, `replay_results.csv`, `repeatability.csv`, `independent_reference/comparison.csv` | Archive counters/mapping pass; three replays exact; 63 reference comparisons consistent | The archived synthetic KPI extraction and declared representative configurations are reproducible and independently checked | No physical ground truth; terminal loss differs from FlowMonitor lostPackets at the 10 s cutoff |
| R3-3: LLM framework insufficiently evaluated (wireless correctness aspect) | Rebuild archived generated source and compare against a separate stock-API reference | `replays/*/compile.log`, `independent_reference/reference.cc` and report | Representative source executes and agrees with independent declared configuration | The wireless simulation output is not accepted solely because code compiled; it passed structural/numerical checks | This does not provide missing token/cost/history logs or evaluate the full LLM framework |
| R3-10: ns-3 terminology | Source and output model audit | `ns3_claim_boundary.md`; archived source lines 112-152 | Terminology locked to LTE/EPC, Wi-Fi 802.11n, CSMA LiFi surrogate | Use configuration-specific synthetic claims | No 5G NR or physical LiFi claim is supported |
| R1: dataset summary | Synthetic dataset metadata extraction | `summary.json`, `scenarios.csv`, `artifacts.zip`, metadata table below | 48 runs, 432 app rows, 624 raw rows, parameter coverage and file terms recorded | Add a separate synthetic-wireless dataset row/table | README provides non-commercial academic terms but no SPDX identifier |

### Reviewer 1 metadata material

| Field | Observed value |
| --- | --- |
| Dataset | NS3_Wireless_Hybrid_ParamSweep |
| Source path | /home/ubuntu/Desktop/LLM Driven wireless environment generation/LLM-Driven-Multi-Agent-Optical-Digital-Twin-for-Automated-Data-Generation/NS3_Wireless_Hybrid_ParamSweep |
| Physical testbed | None; synthetic ns-3.44 discrete-event scenario |
| Simulation duration | 10 s per run |
| Sampling interval | N/A; packet-level event-driven simulation |
| Run/configuration count | 48 (4 loads × 2 speeds × 2 LiFi rates × 3 seeds) |
| Application records | 432 (9 application flows × 48 runs) |
| Raw FlowMonitor rows | 624 (13 rows × 48 runs; 9 application + 4 infrastructure/control) |
| Application features | tx/rx/lost packets; throughput; mean delay; mean jitter; configuration fields |
| Branches | LTE/EPC; Wi-Fi 802.11n; CSMA-based LiFi surrogate |
| Labels | No external ground-truth labels; congestion_risk is deterministic postprocessing |
| Archived output files | 48 generated.cc, 48 FlowMonitor XML, 48 kpi.csv, 48 build logs, 48 run logs, plus prompts/reviews/scenario/status JSON |
| Files | CSV, JSON, FlowMonitor XML, C++, logs, ZIP |
| Archive size | 801215 bytes compressed; 4891304 bytes member payload |
| Missing/nonfinite compact cells | 0 blank cells; 0 nonfinite relevant numeric cells |
| Terms | README says academic research/non-commercial use; no SPDX identifier located |

The wireless synthetic table is separate from any real wireless measurement campaign. `scenarios.csv` has 58 columns and SHA-256 a9317161880af38993077da5b85712a6a3b4e259bf46b717485ff3f7e0262f4a; `artifacts.zip` has 432 members (4891304 uncompressed payload bytes). The repository README states academic research/non-commercial use at `/home/ubuntu/Desktop/LLM Driven wireless environment generation/LLM-Driven-Multi-Agent-Optical-Digital-Twin-for-Automated-Data-Generation/README.md:118-119`; no formal SPDX identifier was found in the inspected wireless project materials.

## 12. Exact recommendation for manuscript revision

1. Add the W1 independent correctness evidence as a reproducibility subsection or supplementary table: archive-wide XML recomputation, three representative replays, same-seed repeatability, and the hand-written stock-ns-3 reference.
2. Replace generic or universal wireless ranking statements with the bounded wording in `ns3_claim_boundary.md`. Use LTE/EPC, Wi-Fi 802.11n, and CSMA-based LiFi surrogate consistently.
3. State that the 48-run wireless artifact is synthetic, packet-level ns-3.44 output with 3 CPEs, 9 application flows per run, 10 s duration, loads 2/5/10/20 Mbps, speeds 0.5/3 m/s, LiFi-surrogate rates 50/100 Mbps, and seeds 1/2/3.
4. Rename or explicitly qualify `packet_loss_ratio` as FlowMonitor loss ratio, and state that `tx-rx` terminal accounting is not identical at the exact simulation stop. If the paper requires terminal end-to-end loss, a separate grace-period rerun/re-export is needed; W1 did not alter the archived data.
5. Correct the released metadata so the expanded parameters are the canonical scenario fields, or make the recorded CLI command the formal source of truth. Do not run an expanded source with its stale defaults and call it the corresponding variant.
6. Keep the physical LiFi limitation explicit: the current branch has no optical geometry or calibrated optical channel. Report its low-jitter/high-throughput behaviour only as an observed property of the idealized CSMA surrogate.

### Regeneration decision

**DATASET_REGENERATION_REQUIRED:** not required to establish current FlowMonitor extraction, structural mapping, representative replay, or same-build repeatability. It is conditionally required only if the manuscript intends to claim terminal packet loss rather than FlowMonitor loss, or if authors choose to eliminate the stale base-field metadata instead of documenting/repairing the export manifest. No old result was silently patched.

## Final status

W1_NS3_VERDICT=PASS_WITH_LIMITATIONS
FLOWMONITOR_RECOMPUTATION=PASS_APPLICATION_ROWS_WITH_XML_SERIALIZATION_LIMITATION_AND_EXPLICIT_LOSS_ACCOUNTING_GAP
SWEEP_CONSISTENCY=PASS_STRUCTURAL_48_RUN_432_APPLICATION_FLOW_MAPPING;_METADATA_DEFAULT_MISMATCH_RECORDED
REPRESENTATIVE_REPLAY=PASS_3_OF_3_REBUILT_EXECUTED_9_FLOWS_EACH_EXACT_NUMERICAL_MATCH
SAME_SEED_REPEATABILITY=PASS_ZERO_KPI_DELTA_FOR_TWO_MEDIUM_RUNS
INDEPENDENT_REFERENCE=PASS_9_FLOWS_63_METRICS_CONSISTENT
DATASET_REGENERATION_REQUIRED=NO_FOR_CURRENT_FLOWMON_EVIDENCE;CONDITIONAL_FOR_TERMINAL_LOSS_OR_METADATA_REPAIR
SUPPORTED_WIRELESS_CLAIMS=BOUNDED_SYNTHETIC_NS3_44_LTE_EPC_WIFI_80211N_AND_CSMA_LIFI_SURROGATE_REPRODUCIBILITY
UNSUPPORTED_WIRELESS_CLAIMS=5G_NR_PHYSICAL_LIFI_UNIVERSAL_TECHNOLOGY_RANKING_MEASURED_WIRELESS_VALIDATION_ZERO_TERMINAL_LOSS
READY_FOR_MANUSCRIPT_REVISION=YES_WITH_THE_ABOVE_CLAIM_BOUNDARY_AND_METADATA_CAVEATS
