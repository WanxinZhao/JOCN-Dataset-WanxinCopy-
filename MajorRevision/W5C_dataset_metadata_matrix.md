# W5C dataset and release metadata matrix

This matrix is limited to datasets or derived evaluation artifacts that the
current manuscript presents as released, used, or generated. Values are
classified as **SUPPORTED**, **AUTHOR_CONFIRMATION_REQUIRED**, or
**NOT_APPLICABLE**. No legal licence, physical unit, external URL, date, or
record count is inferred where the current artifacts do not establish it.

## Matrix

| Dataset name | Practical / synthetic / derived | Domain | Acquisition or generator | Duration / time coverage | Records | Features / labels | Units | Format | Approx. size | Licence / terms | Repository / path | Version / snapshot | Known limitations |
|---|---|---|---|---|---:|---|---|---|---:|---|---|---|---|
| 339-km NDFF / Voyager 2023--2024 | Practical processed optical | Optical transport | Earlier Voyager campaign on the 339-km Bristol--Power Gate loop | 2023-12-26 to 2024-01-26 | 1,373 processed records | `Date`, four BER channels, four derived Q-factor columns | BER is a ratio; Q-factor follows the released conversion | CSV | 147,537 B | Practical-repository README: academic, non-commercial; no SPDX file | `OTN Monitoring Data_one_month/Voyager_onemonth_15minsampling.csv` | Public LFS object SHA-256 `9cc61219ee29f48975257a0a556e6c69b12fa0af17552a0984b5a9abb5d78608` | 10-s raw acquisition was resampled to 15 min; this is not the E1/E2 optical source |
| 339-km NDFF / Voyager Christmas 2025 | Practical raw optical | Optical transport | Separate later campaign on the same 339-km NDFF loop | Real timestamps 2025-12-22 16:38:43 to 2026-01-24 16:10:55; no shift or anonymisation | 20,999 physical lines; 20,960 valid telemetry records after removing 38 embedded headers | `Timestamp` plus eight `Voyager_ch*_BER`; Q-factor is derived by E1/E2; no independent service labels | BER is a dimensionless ratio | Raw CSV; derived Q table and cleaning are code-reconstructable | 1,789,223 B | Practical-repository README: academic, non-commercial; no SPDX file | Public `OTN Monitoring Data_one_month/NDFF_Voyager_Christmas_2025/`; local mirror `semantic_case_v6/data/voyager.csv` | SHA-256 `879d7b6143b04b995165360d1600b81b8134312fed08b2bdeb577b5cb8b6e209` | Mostly 70--72-s intervals with larger acquisition gaps; no 15-min resampling; source used by E1/E2 |
| 986-km NDFF QoT | Practical optical | Optical transport | Cited external field-trial dataset, `YangOFC2023` | **AUTHOR_CONFIRMATION_REQUIRED**: campaign period and timestamp coverage not present locally | **AUTHOR_CONFIRMATION_REQUIRED** | Manuscript describes two links, ROADM nodes, multi-channel Q-factor measurements | **AUTHOR_CONFIRMATION_REQUIRED** | Two CSV files are described; files are not in current checkout | **AUTHOR_CONFIRMATION_REQUIRED** | **AUTHOR_CONFIRMATION_REQUIRED** | External release/source path not present locally; citation `YangOFC2023` | Citation-level evidence only | No primary files locally available for independent count/format/missingness audit |
| Deployed urban fibre sensing | Practical raw/processed sensing | Fibre sensing | Deployed MVB--BDFI and MVB--M Shed links, as described in manuscript | Four-week campaign is documented in manuscript; exact timestamps and record counts **AUTHOR_CONFIRMATION_REQUIRED** | **AUTHOR_CONFIRMATION_REQUIRED** | BER, Q-factor, OSNR, received power, Stokes $S_1$--$S_3$, oscilloscope time/voltage | Polarimeter sampling 97.656 kSa/s is documented; field units for all columns **AUTHOR_CONFIRMATION_REQUIRED** | MAT and CSV, multiple traces described | **AUTHOR_CONFIRMATION_REQUIRED** | **AUTHOR_CONFIRMATION_REQUIRED** | Primary MAT/CSV files are not in current checkout | Citation/manuscript description only | No local primary files, sizes, missing-value statistics, or release path |
| Practical wireless access telemetry | Practical measured telemetry | Wireless access | 5G-CLARITY / REASON multi-access testbed | 2024-10-18 20:21:30 to 2024-10-19 20:21:00 in the current file; approximately one day | 2,849 rows | 46 columns; 5G, Wi-Fi, LiFi traffic/signal/inactivity fields, `service_id`, `wireless_domain`; semantic task labels are derived by `run_e1_e2.py`, not independent measured failure labels | Raw column units and exact field definitions **AUTHOR_CONFIRMATION_REQUIRED** | CSV; scripts available | 787,492 B in current checkout; 790,342 B in ZIP serialization; value cells are identical | **AUTHOR_CONFIRMATION_REQUIRED**; repository has no standard LICENSE/SPDX file in checkout | `semantic_case_v6/data/wireless_real_30s.csv`; `MajorRevision/run_e1_e2.py:123-177` | Current GitHub/ZIP values are cell-identical; line endings differ; W1A records the snapshot hashes | Nominal 30-s data have 2,821 30-s, 23 60-s, and 4 90-s intervals; no missing cells or duplicate timestamps in W1A |
| Constructed optical--wireless interoperability benchmark | Derived constructed benchmark | Cross-domain | `build_optical_aligned()` plus positional sequence mapping and `save_constructed_benchmark()` in `run_e1_e2.py` | Uses wireless timestamps as the constructed sequence index; not contemporaneous optical/wireless time coverage | 2,848 one-step samples: 1,698 train, 560 validation, 570 test, and 20 purged boundary rows | Current/target source-row indices, deterministic wireless semantics, optical BER/Q summaries, training-only label thresholds, current risk fields, and rule-derived next-record targets | Normalised semantic values; BER ratios, Q-factor, timestamps, split, thresholds, and class identifiers are documented for all 52 columns | Materialised CSV plus reconstruction script | 1,599,700 B in the committed LF representation | Revision repository has no formal SPDX licence | `semantic_case_v6/data/cross_domain_fusion_dataset.csv`; `MajorRevision/run_e1_e2.py` | SHA-256 `6f290cddd06836042699a6cff615aff90fb3e30a2d3790e1cdf92d8c01412681`; source hashes in E1/E2 provenance | Positional mapping is not time synchronisation, joint measurement, or physical causal pairing; learned V2/V3 representations remain seed-specific result artifacts rather than fixed columns in this deterministic table |
| Semantic utility result table | Derived evaluation artifact | Wireless semantic evaluation | `MajorRevision/run_e1_e2.py` | Chronological 60/20/20 split; 1,698/560/570 evaluated rows with ten-record purge | Per-seed result rows; exact row count is in the CSV | Representation, task, seed, Accuracy, Balanced Accuracy, Macro-F1, AUROC, AUPRC | Metrics are dimensionless; no raw physical units | CSV | 22,485 B in Croissant metadata | Revision repository has no formal SPDX licence | `MajorRevision/E1_semantic_utility/utility_results_per_seed.csv` | E1 revision artifact; ten seeds; optical source SHA fixed | Derived results, not a raw dataset; labels are rule-derived |
| Privacy attack result table | Derived evaluation artifact | Wireless privacy/utility evaluation | `MajorRevision/run_e1_e2.py` | Same chronological split and purge as E1 | Per-seed attacker/representation/target rows; exact row count is in the CSV | Representation, attacker, target, seed, accuracy, balanced accuracy, Macro-F1 | Metrics are dimensionless | CSV | 85,616 B in Croissant metadata | **AUTHOR_CONFIRMATION_REQUIRED** | `MajorRevision/E2_privacy/privacy_results_per_seed.csv` | E2 revision artifact; ten seeds | Dominant RAT target is severely imbalanced; not a formal privacy guarantee |
| Synthetic GNPy configuration artifact | Synthetic generated artifact | Optical transport | LLM-driven workflow with GNPy execution artifacts | Scenario execution history; exact physical time duration is not a dataset field | 8,192 execution records; 6,144 unique configurations; 6,120 `ok`, 24 no-signal; 96 stratified replay cases | Scenario/configuration fields, GSNR/status, replay differences and warnings | GSNR/OSNR in dB where present; other units follow source configurations | CSV, JSONL logs, frozen requirements, source/config manifests | `unique_configurations.csv` 10,091,783 B; replay results 22,566 B | Revision repository has no formal SPDX licence | `MajorRevision/E4_gnpy_audit/` and `MajorRevision/E5_recovered_gnpy_replay/` | v2.12 commit `7ce665010970f57e46672db1ec0864ae448077e6`; strict GNPy 2.14.2 | v2.12 reproduces 96/96 within 0.00050 dB max GSNR error; strict v2.14.2 differs by 0.628/1.435 dB mean/max and warnings persist |
| Synthetic three-RAT wireless DT dataset | Synthetic generated dataset | Wireless simulation | ns-3.44, CTTC 5G-LENA v4.0.y, native Wi-Fi 802.11ax, equation-driven LOS LiFi/OWC | 10-s simulation runs; sweep metadata per run | 432 application-flow records; 624 raw FlowMonitor rows | 48 configurations; 144 NR, 144 Wi-Fi, 144 LiFi; per-flow KPIs, mappings, scenario metadata, LiFi optical state summaries | KPI and optical-state units are documented in `data_dictionary.csv` | FlowMonitor XML, CSV, JSON/metadata, optical-state CSV | 9,644,759 B for the public W4C bundle | Formal licence/reuse terms not specified in current public repository; no SPDX identifier | `W4C_THREE_RAT_SWEEP/` in the public dataset repository | ns-3.44; 5G-LENA v4.0.y; loads 2/5/10/20 Mbps, speeds 0.5/3 m/s, FOV 40/70 degrees, seeds 1/2/3 | Uncalibrated to practical testbed; LiFi is equation-driven LOS with stock packet-access abstraction; branch comparisons are configuration-specific |

## Machine-readable metadata already present

`MajorRevision/croissant_metadata.json` documents the two 339-km Voyager
products, processed practical tables, the materialised constructed benchmark,
derived revision artifacts, GNPy replay, and the final W4C release:

- `semantic_case_v6/data/wireless_real_30s.csv`, 787,492 B in the current
  public snapshot;
- the public Christmas 2025 Voyager raw CSV, 1,789,223 B, and the earlier
  2023--2024 15-minute Voyager product, 147,537 B;
- `semantic_case_v6/data/cross_domain_fusion_dataset.csv`, 1,599,700 B in the
  committed LF representation, SHA-256
  `6f290cddd06836042699a6cff615aff90fb3e30a2d3790e1cdf92d8c01412681`;
- `E1_semantic_utility/utility_results_per_seed.csv`, 22,485 B;
- `E2_privacy/privacy_results_per_seed.csv`, 85,616 B;
- `E4_gnpy_audit/unique_configurations.csv`, 10,091,783 B.

- `W4C_THREE_RAT_SWEEP/analysis/final_application_flow_dataset.csv`, 91,708 B;
  the complete W4C bundle is available under
  `W4C_THREE_RAT_SWEEP/` in the public dataset repository.

The JSON-LD file contains selected field mappings and SHA-256 values. It is a
revision artifact, not proof of a formal legal licence. The public W4C bundle
is described through its application-flow, optical-state, validation, and
field-dictionary entries. Exact aggregate metadata for the externally
referenced 986-km and urban-sensing collections remain to be consolidated.

## Release decisions required before submission

1. Supply authoritative source paths and record/size metadata for the 986-km
   and urban sensing datasets, if they are claimed as released here.
2. Confirm units and definitions for the practical wireless columns.
3. Decide and document formal licence/reuse terms for the revision/W4C
   repository and, if desired, add an SPDX identifier to the practical data.
