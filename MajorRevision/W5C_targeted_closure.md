# W5C targeted P0 closure (updated after source and replay recovery)

## Executive verdict

The original W5C-A audit was subsequently superseded by the E5 GNPy replay,
the public W4C release, and author confirmation of the Christmas 2025 Voyager
campaign. No semantic retraining was required because the public source is
byte-identical to the E1/E2 provenance hash.

The five W5B P0 items are now handled as follows:

| P0 item | W5C-A result |
|---|---|
| Optical date/sampling lineage | Closed. The manuscript and metadata distinguish the earlier 2023--2024 15-minute product from the separate 20,960-record Christmas 2025 E1/E2 source on the same 339-km loop. |
| z1-z8 mapping | Closed for the current implementation. The manuscript now gives the deterministic definitions and the report gives the complete raw-column mapping. |
| Label endogeneity/fusion boundary | Closed for the bounded claim. The manuscript now separates split leakage control from rule-derived target endogeneity and states that no incremental fusion gain is established without a matched raw-wireless-only ablation. |
| Complete point-by-point response | The response contains all 31 comments, and the original reviewer text confirms that R3C4 is the generated-data correctness comment covering both GNPy and wireless evidence. |
| Release metadata | Voyager, constructed-fusion, GNPy-replay, and W4C public paths are closed. External collection totals, undocumented wireless units, and formal licence terms remain explicit limitations. |

The updated result is **targeted closure achieved for the current bounded
scientific claims**. R1C1, R3C1, and R3C4 are closed by the confirmed source,
materialised benchmark, and E5 replay. R1C3 remains partially closed only for
external metadata/terms, while unavailable historical LLM traces are reported
as such. No new experiment is required for the current bounded claims.

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
| 339-km NDFF / Voyager Christmas 2025 | **OBSERVED AND AUTHOR-CONFIRMED**: public raw file and `semantic_case_v6/data/voyager.csv` | Real timestamps `2025-12-22 16:38:43` to `2026-01-24 16:10:55`; no shift/anonymisation | About 33 days on the same 339-km loop as the earlier campaign | 20,999 physical lines including 38 embedded headers | 20,960 valid rows after header/timestamp/BER filtering | Mostly 70--72 s; larger gaps occur | Eight BER columns; Q derived by `sqrt(2)*erfcinv(2*BER)`; no 15-min resampling | Public byte-identical SHA-256 `879d7b6143b04b995165360d1600b81b8134312fed08b2bdeb577b5cb8b6e209` | `CLOSED` |
| 986-km NDFF QoT dataset | **MISSING** in current checkout; cited as `YangOFC2023` | **AUTHOR_CONFIRMATION_REQUIRED** | **AUTHOR_CONFIRMATION_REQUIRED** | **AUTHOR_CONFIRMATION_REQUIRED** | **AUTHOR_CONFIRMATION_REQUIRED** | **AUTHOR_CONFIRMATION_REQUIRED** | Manuscript-level description of two links/ROADM nodes; exact source/preparation not local | No unsupported count/date added | Secondary description only; release lineage **AUTHOR_CONFIRMATION_REQUIRED** |
| Deployed urban fibre sensing | **MISSING** MAT/CSV source files in current checkout | **AUTHOR_CONFIRMATION_REQUIRED** | Four weeks is stated in manuscript secondary description | **AUTHOR_CONFIRMATION_REQUIRED** | **AUTHOR_CONFIRMATION_REQUIRED** | 97.656 kSa/s polarimeter rate stated; other rates **AUTHOR_CONFIRMATION_REQUIRED** | MAT/CSV traces and Stokes/BER/Q/OSNR/power fields described; filtering not locally auditable | No new counts or dates invented | Secondary description only; primary release lineage **AUTHOR_CONFIRMATION_REQUIRED** |
| Derived optical table for E1/E2 | **OBSERVED**: materialised by `build_optical_aligned()` | Inherits current Voyager source values; not a contemporaneous paired period | 2,849 wireless-indexed rows before one-step shift | 20,960 optical source rows available to positional selection | 2,848 benchmark samples after target shift | Wireless index timestamps are assigned; no native optical resampling | Repeated headers/timestamp/BER filtering; positional `round(linspace(...))` mapping | `semantic_case_v6/data/cross_domain_fusion_dataset.csv` plus reconstruction script | Released; constructed-boundary limitation retained |
| Synthetic GNPy artifact | **OBSERVED**: E4 audit plus E5 replay | Scenario execution history; no physical sampling period | Execution duration not a dataset field | 8,192 execution records | 6,144 unique; 96 stratified replay cases | Scenario-dependent | Deduplication, warning scan, v2.12 compatibility replay, v2.14.2 strict-schema replay | 96/96 complete in both arms; mean/max GSNR error 0.00015/0.00050 dB for v2.12 and 0.628/1.435 dB for v2.14.2 | `CLOSED_WITH_MODEL_LIMITATIONS` |

The manuscript now identifies both products explicitly: the 2023--2024
1,373-record 15-minute product and the separate Christmas 2025 E1/E2 source.
Their dates, channel counts, sampling, public paths, and roles are not mixed.

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

The GNPy track now has two explicit numerical replays. The historical
v2.12-compatible environment at commit
`7ce665010970f57e46672db1ec0864ae448077e6` reproduced all 96 channel records
with mean/max absolute GSNR errors of 0.00015/0.00050 dB. A strict replay with
GNPy 2.14.2 also completed all 96 records, but produced larger mean/max
differences of 0.628/1.435 dB. The manuscript therefore claims reproducibility
for the pinned historical environment and reports the newer-version mismatch
as model/version sensitivity rather than concealing it.

## 7. Complete response and partial-comment reassessment

Current update (2026-09-11): the original reviewer attachment is available,
and the R1/R2/R3 identifiers have been checked against it. The next paragraph
is retained only as the historical W5C-A record; its statement that the letter
was unavailable and its identifier-check request are superseded.

`W5C_complete_point_by_point_response.md` contains R1C1--R1C3,
R2C1--R2C16, and R3C1--R3C12 exactly once. It gives concrete manuscript
locations and evidence rather than generic “revised” statements. The local
materials do not contain the original reviewer letter; therefore the response
labels the comment text as normalized from
`MajorRevision/06_审稿意见处理状态.md` and requests a final identifier check.

| W5B partial comment | Current status | Reason |
|---|---|---|
| R1C1 | `CLOSED` | The two 339-km Voyager campaigns are separated, the Christmas 2025 raw source is public, and the constructed-pairing limitation is explicit. |
| R1C2 | `CLOSED_WITH_UNAVAILABLE_HISTORICAL_TRACE` | Source defaults and retry policy are documented; unavailable historical per-call traces are disclosed instead of reconstructed. |
| R1C3 | `PARTIALLY_CLOSED` | Voyager, W4C, GNPy, and fusion artifacts are public/machine-readable; exact external sensing metadata, practical-wireless units, and formal licence terms still require owners. |
| R2C9 | `CLOSED` | Exact deterministic z1-z8 mapping, train-only fitting scope, and confidence interpretation are now documented. |
| R2C14 | `CLOSED` | Complete response states the qualitative role decomposition and unmeasured communication overhead; no efficiency claim is made. |
| R3C1 | `CLOSED` | Leakage control, semantic mapping, the materialised fusion table, and the exact optical source distinction are documented. |
| R3C3 | `CLOSED` | Complete response separates LLM-architecture evidence from generated-data correctness and discloses missing historical logs. |
| R3C4 | `CLOSED_WITH_DECLARED_MODEL_LIMITATIONS` | W4C is public and the pinned GNPy environment reproduces the released values; the current-version mismatch is reported quantitatively. |

## 8. Build verification

The edited manuscript was rebuilt from the checked-out paper repository with:

```text
latexmk -pdf -interaction=nonstopmode -file-line-error JOCN_Telemetry.tex
```

The command exited with code 0 and generated `JOCN_Telemetry.pdf` (14 pages).
The final log contains no undefined citation, undefined reference, LaTeX
error, or emergency-stop diagnostic, and no new `Overfull \\hbox` warning was
introduced by the W5C edits. Existing non-fatal underfull-box, font-shape,
package-name, and PDF page-group warnings remain outside this targeted task.

## 9. No-experiment statement

No semantic retraining, ns-3 run, or new optical acquisition was needed in
this closure pass. The existing E5 evidence supplies both pinned and current
GNPy replays. A fusion ablation is required only if the authors later add an
incremental fusion-gain claim; the current manuscript makes only a bounded
interoperability/feasibility claim.

W5C_VERDICT=TARGETED_P0_CLOSURE_WITH_RESIDUAL_EXTERNAL_METADATA_ITEMS
P0_OPTICAL_LINEAGE_STATUS=CLOSED_TWO_339KM_CAMPAIGNS_SEPARATED_AND_PUBLIC_SOURCES_IDENTIFIED
P0_Z1_Z8_MAPPING_STATUS=CLOSED_EXACT_DETERMINISTIC_MAPPING_DOCUMENTED
P0_LABEL_ENDOGENEITY_STATUS=CLOSED_FOR_BOUNDED_CLAIM_RULE_DERIVED_NEXT_RECORD_TARGETS_EXPLICIT
P0_FUSION_CLAIM_STATUS=CLOSED_FOR_NARROW_CONSTRUCTION_CLAIM_NO_INCREMENTAL_GAIN_CLAIM
P0_POINT_BY_POINT_RESPONSE_STATUS=COMPLETE_31_COMMENT_DOCUMENT_CREATED_AND_IDENTIFIERS_CHECKED
P0_RELEASE_METADATA_STATUS=MACHINE_READABLE_CORE_RELEASE_COMPLETE; EXTERNAL_SENSING_METADATA_WIRELESS_UNITS_AND_FORMAL_TERMS_AUTHOR_CONFIRMATION_REQUIRED
CROSS_DOMAIN_PAIRING_STATUS=CONSTRUCTED_SEQUENCE_ALIGNED_INTEROPERABILITY_BENCHMARK_NOT_CONTEMPORANEOUS_MEASUREMENT
LLM_SUPERIORITY_CLAIM_STATUS=NOT_MADE; FEASIBILITY_ONLY
GNPY_VALIDATION_CLAIM_STATUS=PINNED_HISTORICAL_REPLAY_MATCHES; CURRENT_2_14_2_VERSION_SENSITIVITY_QUANTIFIED
STRICT_BUILD_STATUS=PASS_LATEXMK_EXIT_0_PDF_14_PAGES_UNDEFINED_CITATIONS_0_UNDEFINED_REFERENCES_0_NO_NEW_OVERFULL_BOX
PARTIAL_COMMENTS_CLOSED=R1C1;R1C2;R2C9;R2C14;R3C1;R3C3;R3C4
COMMENTS_BLOCKED_ON_AUTHOR_CONFIRMATION=NONE
STILL_PARTIAL_COMMENTS=R1C3
NEW_EXPERIMENTS_RUN=GNPY_E5_REPLAY_ALREADY_AVAILABLE_AND_INTEGRATED
NEW_EXPERIMENTS_REQUIRED_FOR_CURRENT_CLAIMS=NO
AUTHOR_CONFIRMATION_ITEMS=EXACT_986KM_AND_SENSING_METADATA;PRACTICAL_WIRELESS_UNITS;FORMAL_LICENCE_SPDX;HISTORICAL_LLM_PER_CALL_TRACES_IF_ANY
READY_FOR_W5C_B_FINALIZATION=YES_WITH_RESIDUAL_ITEMS_EXPLICITLY_RETAINED_AS_LIMITATIONS
