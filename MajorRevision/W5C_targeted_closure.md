# W5C-A targeted P0 closure

## Executive verdict

W5C-A made only targeted evidence-alignment edits. No simulation, ML run,
semantic retraining, ns-3 execution, GNPy execution, or new optical analysis
was performed. The wireless W4C/W4D/W4E evidence remains frozen.

The five W5B P0 items are now handled as follows:

| P0 item | W5C-A result |
|---|---|
| Optical date/sampling lineage | The manuscript no longer presents the unsupported 2023/10-s/15-min lineage as the current Voyager file's fact. File-level observations are reported; unresolved campaign/product identity is isolated in `W5C_author_confirmation_required.md`. |
| z1-z8 mapping | Closed for the current implementation. The manuscript now gives the deterministic definitions and the report gives the complete raw-column mapping. |
| Label endogeneity/fusion boundary | Closed for the bounded claim. The manuscript now separates split leakage control from rule-derived target endogeneity and states that no incremental fusion gain is established without a matched raw-wireless-only ablation. |
| Complete point-by-point response | A new response document contains all 31 normalized comments exactly once, with response, manuscript location, evidence, and limitations. Original reviewer text was unavailable locally, so the author must verify the normalized wording and especially the R3C4 identifier. |
| Release metadata | A definitive matrix and short author questionnaire were created. No licence, unit, source path, date, or count was invented. Release-critical unknowns remain explicitly author-confirmation items. |

The overall W5C-A result is therefore **targeted closure achieved for the
current bounded scientific claims, with four comments blocked on author facts
and one comment still partial because the GNPy numerical replay evidence is
not available**. No new experiment is required for the current bounded
claims.

## Evidence conventions

- **OBSERVED**: read directly from current code, artifact, manuscript, or
  revision evidence.
- **INFERRED**: interpretation of observed implementation or relationships.
- **MISSING**: the available artifacts do not establish the fact.
- **AUTHOR_CONFIRMATION_REQUIRED**: a factual or release decision must be
  supplied by the authors; it is not inferred here.

## 1. Optical date and sampling lineage

The current semantic code reads
`/tmp/jocn-w0-github/semantic_case_v6/data/voyager.csv` in
`build_optical_aligned()` at
`/tmp/jocn-w0-github/MajorRevision/run_e1_e2.py:180-210`. It removes repeated
header rows, parses and sorts `Timestamp`, retains rows with at least one BER
value, computes Q-factor from BER, and maps ordered optical rows to wireless
rows by relative sequence position. It does not resample to 15 minutes.

| Dataset | Raw source | Raw time period | Reported duration | Raw sample count | Processed sample count | Sampling interval / rate | Derivation / filtering | Current wording and evidence | Status |
|---|---|---|---|---:|---:|---|---|---|---|
| 339-km NDFF / Voyager optical telemetry | **OBSERVED**: `semantic_case_v6/data/voyager.csv` | **SUPPORTED_BY_PRIMARY_DATA**: `2025-12-22 16:38:43` to `2026-01-24 16:10:55` in valid rows | About 33 days of file timestamp coverage; physical campaign duration **AUTHOR_CONFIRMATION_REQUIRED** | 20,998 CSV data rows before cleaning | 20,960 valid rows after repeated-header, timestamp, and BER filtering | Mostly 70--72 s; median about 71 s; larger gaps occur | Eight BER columns; BER numeric conversion, clipping, Q via `sqrt(2)*erfcinv(2*BER)`; no 15-min resampling in current code | Manuscript now reports file-level facts and does not identify this file as a 10-s product resampled to 15 min | File facts supported; physical product/date lineage **AUTHOR_CONFIRMATION_REQUIRED** |
| 986-km NDFF QoT dataset | **MISSING** in current checkout; cited as `YangOFC2023` | **AUTHOR_CONFIRMATION_REQUIRED** | **AUTHOR_CONFIRMATION_REQUIRED** | **AUTHOR_CONFIRMATION_REQUIRED** | **AUTHOR_CONFIRMATION_REQUIRED** | **AUTHOR_CONFIRMATION_REQUIRED** | Manuscript-level description of two links/ROADM nodes; exact source/preparation not local | No unsupported count/date added | Secondary description only; release lineage **AUTHOR_CONFIRMATION_REQUIRED** |
| Deployed urban fibre sensing | **MISSING** MAT/CSV source files in current checkout | **AUTHOR_CONFIRMATION_REQUIRED** | Four weeks is stated in manuscript secondary description | **AUTHOR_CONFIRMATION_REQUIRED** | **AUTHOR_CONFIRMATION_REQUIRED** | 97.656 kSa/s polarimeter rate stated; other rates **AUTHOR_CONFIRMATION_REQUIRED** | MAT/CSV traces and Stokes/BER/Q/OSNR/power fields described; filtering not locally auditable | No new counts or dates invented | Secondary description only; primary release lineage **AUTHOR_CONFIRMATION_REQUIRED** |
| Derived optical table for E1/E2 | **OBSERVED**: constructed in memory by `build_optical_aligned()` | Inherits current Voyager source values; not a contemporaneous paired period | 2,849 wireless-indexed rows before one-step shift | 20,960 optical source rows available to positional selection | 2,848 benchmark samples after target shift | Wireless index timestamps are assigned; no native optical resampling | Repeated headers/timestamp/BER filtering; BER clipping; positional `round(linspace(...))` mapping | Described as a constructed sequence-aligned benchmark, not a released joint measurement | Code-reconstructable; standalone release path **AUTHOR_CONFIRMATION_REQUIRED** |
| Synthetic GNPy artifact | **OBSERVED**: `MajorRevision/E4_gnpy_audit/` | Scenario execution history; no single physical sampling period | Execution duration not a dataset field | 8,192 execution records | 6,144 unique; 6,120 `ok`, 24 no-signal | Scenario-dependent | Deduplication, status/warning scan, and independent preparation audit | Wording is limited to artifact coverage, uniqueness, warnings, and feasibility | `PARTIAL`: numerical replay unavailable without original environment |

The current manuscript's optical subsection now makes the important
distinction between a timestamp range observed in the released CSV and the
physical campaign date. The W1A conflict is not silently resolved. The
questionnaire requests the original campaign/product confirmation and the
source of any 10-s or 15-minute product.

## 2. Definitive z1-z8 reconstruction

The source of truth is `build_wireless_base()` and `derive_semantics()` in
`MajorRevision/run_e1_e2.py:123-276`; V1 selects the eight columns at
`run_e1_e2.py:674-677`. All values below are deterministic; none is a learned
latent. `MM_train(x)` means `(x-min_train)/(max_train-min_train)` fitted only
on training rows, followed by clipping to `[0,1]`. `clip` below is the same
`[0,1]` clipping in the implementation.

| Semantic field | Symbol | Exact source feature(s) | Transformation | Unit / normalized status | Interpretation |
|---|---|---|---|---|---|
| `wireless_load_score` | z1 | `total_wireless_traffic`; this is the row sum of the ten 5G columns, sixteen Wi-Fi traffic columns, and four LiFi traffic columns listed below. | `clip(MM_train(total_wireless_traffic))`. | Unit not recorded in the CSV; normalized to `[0,1]`. | Relative aggregate wireless load. |
| `link_stability_score` | z2 | z7, z6, z8. | `clip(0.5*z7 + 0.3*(1-z6) + 0.2*(1-z8))`. | `[0,1]`; deterministic composite. | Signal/stability score where fluctuation and inactivity reduce the score. |
| `access_diversity_score` | z3 | `active_5g`, `active_wifi`, `active_lifi`, derived from `traffic_5g`, `traffic_wifi`, `traffic_lifi`. | `(active_5g+active_wifi+active_lifi)/3`; each active flag is `traffic_rat > train_q25(traffic_rat)`. | `[0,1]`; dimensionless fraction. | Fraction of access branches active relative to train-derived thresholds. |
| `congestion_risk` | z4 | z1, z2, z3, z6, z8. | `sigmoid(2*z1 + 1.5*z8 + z6 - 1.5*z2 - 0.8*z3)`. | Logistic output in `(0,1)`; deterministic risk score. | Composite congestion-risk indicator, not observed congestion ground truth. |
| `traffic_rolling_mean_score` | z5 | Five-record backward rolling mean `R5(total_wireless_traffic)`. | `clip(MM_train(R5(total_wireless_traffic)))`; `min_periods=1`. | Unit not recorded; normalized to `[0,1]`. | Relative recent traffic level. |
| `traffic_fluctuation_score` | z6 | Five-record backward rolling sample standard deviation `F5(total_wireless_traffic)`. | `clip(MM_train(F5(total_wireless_traffic)))`; `min_periods=1`, initial NaN filled with zero. | Unit not recorded; normalized to `[0,1]`. | Relative short-window traffic variability. |
| `signal_quality` | z7 | `wifi_signal_mean` = row mean of `signalAvg_CPE1_WiFi` through `signalAvg_CPE4_WiFi`; `lifi_signal` = `signal_CPE4_LiFi`. | `clip(0.7*MM_train(wifi_signal_mean)+0.3*MM_train(lifi_signal))`. | `[0,1]`; raw signal units are not retained. | Weighted wireless signal-quality indicator. |
| `inactivity_risk` | z8 | `wifi_inactivity_mean` = row mean of `inactiveTime_CPE1_WiFi` through `inactiveTime_CPE4_WiFi`. | `clip(MM_train(wifi_inactivity_mean))`. | Unit not recorded; normalized to `[0,1]`. | Relative Wi-Fi inactivity risk. |

The exact raw column groups are:

- `traffic_5g`: `Total 5G Cell Uplink Traffic`, `Total 5G Cell Downlink
  Traffic`, and `recv_`/`trans_` columns for CPE1--CPE4 on 5G.
- `traffic_wifi`: `rxBytes_`/`txBytes_` columns for CPE1--CPE4 on Wi-Fi and
  `recv_`/`trans_` columns for CPE1--CPE4 on Wi-Fi.
- `traffic_lifi`: `txBytes_CPE4_LiFi`, `rxBytes_CPE4_LiFi`,
  `trans_CPE4_lifi`, and `recv_CPE4_lifi`.
- signal and inactivity groups are the exact eight columns named in the z7
  and z8 rows; `signal_CPE4_LiFi` is the sole LiFi signal input.

`semantic_confidence` is not a ninth learned semantic field. The exact code
is `semantic_confidence = clip(1 - traffic_fluctuation_score, 0, 1)` at
`derive_semantics()`. It is a deterministic fluctuation-derived confidence
heuristic, not a calibrated probability, posterior, or uncertainty
estimate. All thresholds and min--max ranges are fit on training rows only;
the rolling features are backward-looking and the ten-record purge is
retained.

## 3. Label endogeneity and target validity

| Target | Observed or derived | Source variables and rule | Temporal shift | Source variables in model input? | Field ground truth? | Defensible claim |
|---|---|---|---|---|---|---|
| Binary service risk | Derived | `optical_risk OR wireless_risk`; optical risk is `q_factor < train 15th percentile` or `ber > train 85th percentile`; wireless risk is `C>0.65 OR S<0.35 OR D<0.34`. | Target at next record: arrays use `[1:]`, current features use `[:-1]`. | Yes: optical BER/Q summaries and wireless semantic quantities or reconstructions are included in the evaluated representations. | No. | Constructed next-record service-risk recoverability benchmark. |
| Four-class degradation source | Derived | Class 0 neither, 1 wireless-only, 2 optical-only, 3 both, from the same two rules. | Same one-record shift. | Yes, through the same optical and wireless quantities. | No. | Constructed source-of-rule classification, not physical fault diagnosis. |
| Congestion risk | Derived semantic score | `sigmoid(2z1+1.5z8+z6-1.5z2-0.8z3)`. | Used as a current-record semantic target and in the wireless-risk rule; downstream targets are shifted where applicable. | Yes or reconstructed for the relevant representation. | No. | Deterministic engineering score. |
| Dominant CPE | Derived privacy attribute | `idxmax` over `private_CPE1`--`private_CPE4`, which are sums of per-CPE traffic columns. | Current record is used as the next-record privacy target. | Related aggregate traffic fields are present in raw/private representations. | No. | Attribute-inference diagnostic on a constructed target. |
| Dominant RAT | Derived privacy attribute | `idxmax` over `private_5G`, `private_WiFi`, `private_LiFi`. | Current record is used as the next-record privacy target. | Related aggregate traffic fields are present in raw/private representations. | No. | Imbalanced attribute-inference diagnostic; not evidence of formal privacy. |

This is a label-validity limitation, not a split-leakage finding. The
chronological split and train-only preprocessing control conventional
held-out-statistic leakage, but the target construction remains endogenous
to related telemetry. The manuscript now states this explicitly and does
not call these labels observed failures or field ground truth.

## 4. Fusion and pairing boundary

The code path is `build_optical_aligned()` followed by positional mapping
with `round(linspace(0, len(optical)-1, num=len(wireless_times)))`. The optical
and wireless timestamp ranges do not overlap. The manuscript now uses
``constructed optical--wireless interoperability benchmark`` and states that
there is no timestamp equality, simultaneous campaign, physical causal
claim, or optical-to-wireless signal conversion.

The available utility methods are `OpticalOnly`,
`WirelessSemanticOnly_V3`, `RawWirelessPlusOptical`, and related semantic-plus-
optical representations. A matched `RawWirelessOnly` method is absent. The
current evidence therefore supports construction and evaluation of
cross-domain representations, not an incremental causal or predictive gain
from fusion. No fusion experiment was run in W5C-A.

## 5. Release metadata closure

The definitive matrix is in `W5C_dataset_metadata_matrix.md`. It separates
practical, synthetic, and derived artifacts, records supported counts and
formats, and marks unknown licences, physical units, external source paths,
and unresolved optical lineage as `AUTHOR_CONFIRMATION_REQUIRED`.

The current manuscript table was minimally corrected to:

- report current Voyager file timestamps and observed intervals rather than
  unsupported 10-s/15-min processing;
- distinguish code-reconstructable fusion output from a measured paired file;
- avoid assigning a formal licence where the checkout has no
  LICENSE/SPDX file;
- retain the final W4C synthetic row separately from practical wireless data.

No exact size, licence, date, unit, or external dataset record was invented.

## 6. LLM and GNPy claim boundaries

The current text remains within the observed evidence. It permits an
LLM-driven feasibility claim, deterministic enumeration baseline, and
wireless W4C correctness evidence. It does not claim LLM superiority, lower
cost/latency, or complete historical prompt/token/provider provenance.

The GNPy text permits artifact generation, uniqueness/warning auditing, and
workflow feasibility. It explicitly states that current public GNPy releases
cannot load the released equipment file and that the published numerical
values were not independently replayed. No GNPy command was run in W5C-A.

## 7. Complete response and partial-comment reassessment

`W5C_complete_point_by_point_response.md` contains R1C1--R1C3,
R2C1--R2C16, and R3C1--R3C12 exactly once. It gives concrete manuscript
locations and evidence rather than generic “revised” statements. The local
materials do not contain the original reviewer letter; therefore the response
labels the comment text as normalized from
`MajorRevision/06_审稿意见处理状态.md` and requests a final identifier check.

| W5B partial comment | W5C-A status | Reason |
|---|---|---|
| R1C1 | `BLOCKED_ON_AUTHOR_CONFIRMATION` | Constructed cross-domain wording is corrected, but optical product/campaign date and sampling lineage remain unresolved. |
| R1C2 | `BLOCKED_ON_AUTHOR_CONFIRMATION` | The bounded feasibility response is complete, but unavailable LLM model/log/cost/latency facts must be confirmed as unavailable or supplied if they exist. |
| R1C3 | `BLOCKED_ON_AUTHOR_CONFIRMATION` | Matrix and manuscript table are improved, but external dataset paths and formal release terms are not recoverable locally. |
| R2C9 | `CLOSED` | Exact deterministic z1-z8 mapping, train-only fitting scope, and confidence interpretation are now documented. |
| R2C14 | `CLOSED` | Complete response states the qualitative role decomposition and unmeasured communication overhead; no efficiency claim is made. |
| R3C1 | `BLOCKED_ON_AUTHOR_CONFIRMATION` | Leakage control and semantic mapping are documented, but the optical source/product conflict propagates to the exact E1/E2 snapshot. |
| R3C3 | `CLOSED` | Complete response separates LLM-architecture evidence from generated-data correctness and discloses missing historical logs. |
| R3C4 | `STILL_PARTIAL` | Wireless correctness is closed, but the GNPy track still lacks independent numerical replay; the response states this rather than claiming closure. The original identifier must also be checked. |

## 8. Build verification

The edited manuscript was built from `/tmp/jocn-w0-github` with:

```text
latexmk -pdf -interaction=nonstopmode -file-line-error JOCN_Telemetry.tex
```

The command exited with code 0 and generated `JOCN_Telemetry.pdf` (14 pages).
The final log contains no undefined citation, undefined reference, LaTeX
error, or emergency-stop diagnostic, and no new `Overfull \\hbox` warning was
introduced by the W5C edits. Existing non-fatal underfull-box, font-shape,
package-name, and PDF page-group warnings remain outside this targeted task.

## 9. No-experiment statement

W5C-A ran no simulations, ML experiments, semantic retraining, ns-3,
GNPy, or new optical analysis. Current bounded claims need no new experiment.
An affected E1/E2 rerun is conditional only if authors identify a different
optical primary product; a GNPy rerun is conditional only if independent
numerical reproduction is retained as a requested claim; a fusion ablation
is conditional only if an incremental fusion-gain claim is added.

W5C_VERDICT=TARGETED_P0_CLOSURE_WITH_AUTHOR_BLOCKERS
P0_OPTICAL_LINEAGE_STATUS=MANUSCRIPT_CONFLICT_REMOVED_FROM_ACTIVE_FACT_CLAIM; FILE_FACTS_REPORTED; CAMPAIGN_PRODUCT_LINEAGE_AUTHOR_CONFIRMATION_REQUIRED
P0_Z1_Z8_MAPPING_STATUS=CLOSED_EXACT_DETERMINISTIC_MAPPING_DOCUMENTED
P0_LABEL_ENDOGENEITY_STATUS=CLOSED_FOR_BOUNDED_CLAIM_RULE_DERIVED_NEXT_RECORD_TARGETS_EXPLICIT
P0_FUSION_CLAIM_STATUS=CLOSED_FOR_NARROW_CONSTRUCTION_CLAIM_NO_INCREMENTAL_GAIN_CLAIM
P0_POINT_BY_POINT_RESPONSE_STATUS=COMPLETE_31_COMMENT_DOCUMENT_CREATED; ORIGINAL_LETTER_IDENTIFIER_CHECK_REQUIRED
P0_RELEASE_METADATA_STATUS=COMPLETE_MATRIX_CREATED; EXTERNAL_PATHS_UNITS_AND_FORMAL_TERMS_AUTHOR_CONFIRMATION_REQUIRED
CROSS_DOMAIN_PAIRING_STATUS=CONSTRUCTED_SEQUENCE_ALIGNED_INTEROPERABILITY_BENCHMARK_NOT_CONTEMPORANEOUS_MEASUREMENT
LLM_SUPERIORITY_CLAIM_STATUS=NOT_MADE; FEASIBILITY_ONLY
GNPY_VALIDATION_CLAIM_STATUS=ARTIFACT_AUDIT_ONLY; INDEPENDENT_NUMERICAL_REPLAY_NOT_ESTABLISHED
STRICT_BUILD_STATUS=PASS_LATEXMK_EXIT_0_PDF_14_PAGES_UNDEFINED_CITATIONS_0_UNDEFINED_REFERENCES_0_NO_NEW_OVERFULL_BOX
PARTIAL_COMMENTS_CLOSED=R2C9;R2C14;R3C3
COMMENTS_BLOCKED_ON_AUTHOR_CONFIRMATION=R1C1;R1C2;R1C3;R3C1
STILL_PARTIAL_COMMENTS=R3C4
NEW_EXPERIMENTS_RUN=NO
NEW_EXPERIMENTS_REQUIRED_FOR_CURRENT_CLAIMS=NO
AUTHOR_CONFIRMATION_ITEMS=OPTICAL_CAMPAIGN_PRODUCT_DATE_AND_SAMPLING;EXTERNAL_DATASET_PATHS_COUNTS_AND_TERMS;WIRELESS_UNITS;LLM_LOG_AVAILABILITY;ORIGINAL_REVIEWER_IDENTIFIERS
READY_FOR_W5C_B_FINALIZATION=YES_AFTER_AUTHOR_CONFIRMATION_ITEMS_ARE_RESOLVED_OR_EXPLICITLY_RETAINED_AS_LIMITATIONS
