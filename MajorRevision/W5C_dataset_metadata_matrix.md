# W5C dataset and release metadata matrix

This matrix is limited to datasets or derived evaluation artifacts that the
current manuscript presents as released, used, or generated. Values are
classified as **SUPPORTED**, **AUTHOR_CONFIRMATION_REQUIRED**, or
**NOT_APPLICABLE**. No legal licence, physical unit, external URL, date, or
record count is inferred where the current artifacts do not establish it.

## Matrix

| Dataset name | Practical / synthetic / derived | Domain | Acquisition or generator | Duration / time coverage | Records | Features / labels | Units | Format | Approx. size | Licence / terms | Repository / path | Version / snapshot | Known limitations |
|---|---|---|---|---|---:|---|---|---|---:|---|---|---|---|
| 339-km NDFF / Voyager telemetry | Practical processed optical | Optical transport | Voyager optical telemetry; exact physical campaign/product lineage requires confirmation | **SUPPORTED_BY_PRIMARY_DATA** for current file timestamps: 2025-12-22 16:38:43 to 2026-01-24 16:10:55; physical campaign dates **AUTHOR_CONFIRMATION_REQUIRED** | 20,998 CSV data rows before cleaning; 20,960 valid rows used by current preprocessing | 9 CSV columns: `Timestamp` plus eight `Voyager_ch*_BER`; Q-factor is derived by the revision script; no independent service labels | BER/Q units are not fully documented in current CSV; **AUTHOR_CONFIRMATION_REQUIRED** | CSV; derived Q table is code-reconstructable | 1,768,224 B in the current public snapshot | **AUTHOR_CONFIRMATION_REQUIRED**; no standard LICENSE/SPDX file in current checkout | `semantic_case_v6/data/voyager.csv`; `MajorRevision/run_e1_e2.py:180-210` | Current public snapshot; E1/E2 provenance hash is recorded in revision artifacts | Mostly 70--72 s timestamp intervals, with larger gaps; no evidence in current artifacts for 10-s raw to 15-min resampling |
| 986-km NDFF QoT | Practical optical | Optical transport | Cited external field-trial dataset, `YangOFC2023` | **AUTHOR_CONFIRMATION_REQUIRED**: campaign period and timestamp coverage not present locally | **AUTHOR_CONFIRMATION_REQUIRED** | Manuscript describes two links, ROADM nodes, multi-channel Q-factor measurements | **AUTHOR_CONFIRMATION_REQUIRED** | Two CSV files are described; files are not in current checkout | **AUTHOR_CONFIRMATION_REQUIRED** | **AUTHOR_CONFIRMATION_REQUIRED** | External release/source path not present locally; citation `YangOFC2023` | Citation-level evidence only | No primary files locally available for independent count/format/missingness audit |
| Deployed urban fibre sensing | Practical raw/processed sensing | Fibre sensing | Deployed MVB--BDFI and MVB--M Shed links, as described in manuscript | Four-week campaign is documented in manuscript; exact timestamps and record counts **AUTHOR_CONFIRMATION_REQUIRED** | **AUTHOR_CONFIRMATION_REQUIRED** | BER, Q-factor, OSNR, received power, Stokes $S_1$--$S_3$, oscilloscope time/voltage | Polarimeter sampling 97.656 kSa/s is documented; field units for all columns **AUTHOR_CONFIRMATION_REQUIRED** | MAT and CSV, multiple traces described | **AUTHOR_CONFIRMATION_REQUIRED** | **AUTHOR_CONFIRMATION_REQUIRED** | Primary MAT/CSV files are not in current checkout | Citation/manuscript description only | No local primary files, sizes, missing-value statistics, or release path |
| Practical wireless access telemetry | Practical measured telemetry | Wireless access | 5G-CLARITY / REASON multi-access testbed | 2024-10-18 20:21:30 to 2024-10-19 20:21:00 in the current file; approximately one day | 2,849 rows | 46 columns; 5G, Wi-Fi, LiFi traffic/signal/inactivity fields, `service_id`, `wireless_domain`; semantic task labels are derived by `run_e1_e2.py`, not independent measured failure labels | Raw column units and exact field definitions **AUTHOR_CONFIRMATION_REQUIRED** | CSV; scripts available | 787,492 B in current checkout; 790,342 B in ZIP serialization; value cells are identical | **AUTHOR_CONFIRMATION_REQUIRED**; repository has no standard LICENSE/SPDX file in checkout | `semantic_case_v6/data/wireless_real_30s.csv`; `MajorRevision/run_e1_e2.py:123-177` | Current GitHub/ZIP values are cell-identical; line endings differ; W1A records the snapshot hashes | Nominal 30-s data have 2,821 30-s, 23 60-s, and 4 90-s intervals; no missing cells or duplicate timestamps in W1A |
| Constructed optical--wireless interoperability benchmark | Derived constructed benchmark | Cross-domain | `build_optical_aligned()` plus positional sequence mapping in `run_e1_e2.py` | Uses wireless timestamps as the constructed sequence index; not contemporaneous optical/wireless time coverage | 2,848 one-step samples after target shift | Optical BER/Q summaries, wireless semantic features, rule-derived binary and four-class targets | Normalized semantic values; raw physical units not retained; **AUTHOR_CONFIRMATION_REQUIRED** for full data dictionary | Reconstructable by script; no standalone CSV in current checkout | **AUTHOR_CONFIRMATION_REQUIRED** for released file size | **AUTHOR_CONFIRMATION_REQUIRED** | `MajorRevision/run_e1_e2.py:180-210`, `640-677`; result artifacts under `E1_semantic_utility/` | E1/E2 source snapshot recorded in `provenance.json` | Positional mapping is a constructed interoperability benchmark, not time synchronization, joint measurement, or physical causal pairing |
| Semantic utility result table | Derived evaluation artifact | Wireless semantic evaluation | `MajorRevision/run_e1_e2.py` | Chronological 60/20/20 split; 1,698/560/570 evaluated rows with ten-record purge | Per-seed result rows; exact row count is in the CSV | Representation, task, seed, Accuracy, Balanced Accuracy, Macro-F1, AUROC, AUPRC | Metrics are dimensionless; no raw physical units | CSV | 22,485 B in Croissant metadata | **AUTHOR_CONFIRMATION_REQUIRED** | `MajorRevision/E1_semantic_utility/utility_results_per_seed.csv` | E1 revision artifact; ten seeds | Derived results, not a raw dataset; exact optical source lineage remains tied to author confirmation |
| Privacy attack result table | Derived evaluation artifact | Wireless privacy/utility evaluation | `MajorRevision/run_e1_e2.py` | Same chronological split and purge as E1 | Per-seed attacker/representation/target rows; exact row count is in the CSV | Representation, attacker, target, seed, accuracy, balanced accuracy, Macro-F1 | Metrics are dimensionless | CSV | 85,616 B in Croissant metadata | **AUTHOR_CONFIRMATION_REQUIRED** | `MajorRevision/E2_privacy/privacy_results_per_seed.csv` | E2 revision artifact; ten seeds | Dominant RAT target is severely imbalanced; not a formal privacy guarantee |
| Synthetic GNPy configuration artifact | Synthetic generated artifact | Optical transport | LLM-driven workflow with GNPy execution artifacts | Scenario execution history; exact physical time duration is not a dataset field | 8,192 execution records; 6,144 unique configurations; 6,120 `ok`, 24 no-signal | Scenario/configuration fields and returned GSNR/status values | GSNR in dB where present; other units follow source configuration; full dictionary **AUTHOR_CONFIRMATION_REQUIRED** | CSV plus archived result artifacts | `unique_configurations.csv` 10,091,783 B in current audit bundle | **AUTHOR_CONFIRMATION_REQUIRED** | `MajorRevision/E4_gnpy_audit/unique_configurations.csv` and E4 audit files | Public commit inspected in E4: `f11545c642976607a87b5dc7b9c91b9b8753e0e9`; GNPy working environment not pinned | Warning-bearing artifact; independent numerical replay is not established because public equipment schema fails in tested GNPy versions |
| Synthetic three-RAT wireless DT dataset | Synthetic generated dataset | Wireless simulation | ns-3.44, CTTC 5G-LENA v4.0.y, native Wi-Fi 802.11ax, equation-driven LOS LiFi/OWC | 10-s simulation runs; sweep metadata per run | 432 application-flow records; 624 raw FlowMonitor rows | 48 configurations; 144 NR, 144 Wi-Fi, 144 LiFi; per-flow KPIs, mappings, scenario metadata, LiFi optical state summaries | KPI and optical-state units are documented in `data_dictionary.csv` | FlowMonitor XML, CSV, JSON/metadata, optical-state CSV | 9,644,759 B for the public W4C bundle | Formal licence/reuse terms not specified in current public repository; no SPDX identifier | `W4C_THREE_RAT_SWEEP/` in the public dataset repository | ns-3.44; 5G-LENA v4.0.y; loads 2/5/10/20 Mbps, speeds 0.5/3 m/s, FOV 40/70 degrees, seeds 1/2/3 | Uncalibrated to practical testbed; LiFi is equation-driven LOS with stock packet-access abstraction; branch comparisons are configuration-specific |

## Machine-readable metadata already present

`MajorRevision/croissant_metadata.json` documents the processed practical
tables, derived revision artifacts, and the final W4C release:

- `semantic_case_v6/data/wireless_real_30s.csv`, 787,492 B in the current
  public snapshot;
- `semantic_case_v6/data/voyager.csv`, 1,768,224 B in the current public
  snapshot;
- `E1_semantic_utility/utility_results_per_seed.csv`, 22,485 B;
- `E2_privacy/privacy_results_per_seed.csv`, 85,616 B;
- `E4_gnpy_audit/unique_configurations.csv`, 10,091,783 B.

- `W4C_THREE_RAT_SWEEP/analysis/final_application_flow_dataset.csv`, 91,708 B;
  the complete W4C bundle is available under
  `W4C_THREE_RAT_SWEEP/` in the public dataset repository.

The JSON-LD file contains selected field mappings and SHA-256 values. It is a
revision artifact, not proof of a formal legal licence. The public W4C bundle
is described through its application-flow, optical-state, validation, and
field-dictionary entries. The 986-km or urban sensing primary files and the
standalone constructed-fusion CSV are not included in the current release.

## Release decisions required before submission

1. Confirm the optical Voyager product identity, physical campaign date, and
   relation to any 10-s/15-minute product.
2. Supply authoritative source paths and record/size metadata for the 986-km
   and urban sensing datasets, if they are claimed as released here.
3. Confirm units and definitions for the practical wireless columns.
4. Confirm the public path/version and formal licence or repository terms for
   all claimed files, including the W4C bundle and derived benchmark.
5. Decide whether the constructed benchmark is distributed as a materialized
   file or explicitly released as a code-reconstructable artifact.
