# W5B Manuscript-Wide Reviewer-Comment Closure Audit

> **Superseded status update (2026-09-11).** This file is retained as the
> historical W5B audit. Later evidence closes the former Voyager lineage
> conflict (the 2023--24 processed product and Christmas 2025 raw campaign are
> distinct), materialises the fusion CSV, publishes the W4C bundle, verifies
> the reviewer identifiers, and supplies pinned/current GNPy replays. The
> authoritative current status is
> `W5C_complete_point_by_point_response.md`; remaining author inputs are listed
> in `W5C_author_confirmation_required.md`.

Audit scope: current manuscript and available major-revision evidence only.
No simulation, ML experiment, optical experiment, semantic experiment, or
wireless experiment was run in W5B. No manuscript or reviewer-response text
was modified.

## 1. Executive verdict

The current manuscript is substantially improved, and the final wireless line
is frozen and closed according to W4E. The manuscript does not yet constitute
a complete reviewer-comment closeout because several non-experimental facts
and response-document issues remain.

The most important active-text defect is the optical metadata conflict at
`JOCN_Telemetry.tex:339` and `362-364`: the current primary
`semantic_case_v6/data/voyager.csv` contains valid timestamps from
2025-12-22 through 2026-01-24 with mostly approximately 71-s spacing, while
the manuscript describes a 2023-12-26 through 2024-01-26 campaign with 10-s
raw BER samples resampled to 15 min. W1A found no primary artifact resolving
this conflict. This must be confirmed by the authors before submission.

The semantic leakage-control implementation is materially supported:
chronological splitting, train-only fitted preprocessing, train-only label
thresholds, and a ten-record purge are implemented in
`MajorRevision/run_e1_e2.py`. This does not establish a physical or observed
service-failure target. The labels are deterministic rules derived from the
same optical and semantic quantities used by the downstream models, and the
current results do not provide a matched raw-wireless-only ablation. The
manuscript mostly states this boundary, but the label endogeneity and absence
of an incremental fusion-gain test should be made explicit before making any
stronger fusion claim.

The available materials contain a complete internal status ledger but not the
original reviewer letter or a complete point-by-point response document. The
only current response document is
`MajorRevision/W2_wireless_ns3_reviewer_response.md`, which covers selected
wireless comments and a synthetic-wireless metadata item. In addition, the
ledger labels R3C4 as a GNPy correctness issue, while the W2 response uses
R3C4 for wireless ns-3 correctness. This identifier conflict must be
resolved against the original letter before submission.

### Overall status

| Status | Count | Interpretation |
|---|---:|---|
| CLOSED | 23 | The current bounded claim is supported and no new experiment is required. |
| PARTIALLY_CLOSED | 8 | Evidence or wording addresses the issue, but a factual, metadata, provenance, or response-document gap remains. |
| OPEN | 0 | No comment is wholly unaddressed; the partial items still require targeted closure. |

This is therefore a targeted non-experimental closure stage, not a final
submission-ready verdict.

## 2. Evidence conventions and comment-set provenance

Evidence labels in this audit are:

- **OBSERVED** — directly read from current code, manuscript, artifact, or log.
- **INFERRED** — a scientific interpretation of observed implementation or results.
- **MISSING** — the available materials cannot establish the fact.

The original decision letter and full reviewer PDFs were not present in the
searched `/tmp/jocn-w0-github` checkout or the main research workspace. The
normalized comment set below is therefore recovered from the authoritative
internal ledger `MajorRevision/06_审稿意见处理状态.md:5-49`, not invented from
the manuscript. It contains R1C1-R1C3, R2C1-R2C16, and R3C1-R3C12, for 31
comments. Before submission, the authors should verify the identifiers and
wording against the original letter.

The R3C4 identifier is specifically inconsistent across local documents:
`06_审稿意见处理状态.md:41` describes the GNPy independent-correctness
issue, whereas `W2_wireless_ns3_reviewer_response.md:3-18` uses R3C4 for the
wireless ns-3 correctness concern. This audit lists R3C4 once as the broader
generated-data correctness concern and records both evidence tracks.

## 3. Contribution and organization audit

The active manuscript now presents a coherent hierarchy:

1. practical optical-transport, fibre-sensing, and wireless datasets;
2. semantic representation and privacy/utility evaluation for wireless
   telemetry;
3. an LLM-driven DT workflow demonstrated with GNPy and the final W4C
   three-RAT ns-3 dataset;
4. interoperability and correctness audits supporting those demonstrations.

This is observed at `JOCN_Telemetry.tex:72`, `95-97`, `420-440`, and
`572-574`. The contribution wording is substantially aligned with the
available evidence. In particular, the abstract separates independently
acquired practical data from the constructed benchmark and says that the LLM
workflow is a feasibility demonstration.

The remaining hierarchy risk is not a stale wireless claim. It is that the
paper can still be read as presenting the constructed fusion benchmark as
physical service prediction unless the deterministic rule-derived targets
and the missing matched domain ablation are made more explicit. The current
text says the labels are rule-derived and not field-observed at
`JOCN_Telemetry.tex:276`, but it does not explicitly say that the wireless
risk rule uses semantic quantities also supplied to the model and that the
optical risk rule uses optical features supplied to the model.

## 4. Practical and synthetic dataset metadata audit

The current dataset table is `JOCN_Telemetry.tex:328-347`; the machine-readable
metadata is `MajorRevision/croissant_metadata.json`. The current checkout
contains only `semantic_case_v6/data/wireless_real_30s.csv` and
`semantic_case_v6/data/voyager.csv` as primary data files. The 986-km and
urban-sensing files described in the manuscript are not present in this
checkout, and the Croissant record does not describe them.

| Dataset / artifact | Current evidence | Missing or conflicting metadata | Severity | Minimum action |
|---|---|---|---|---|
| 339-km NDFF / Voyager practical optical telemetry | Table row `JOCN_Telemetry.tex:339`; description `362-364`; primary file `semantic_case_v6/data/voyager.csv`; W1A reports 20,960 valid rows and primary range 2025-12-22--2026-01-24. | Active text says 2023-12-26--2024-01-26, 10-s raw sampling, and 15-min resampling; these are not supported by the current file or scripts. | MATERIAL_FOR_REVIEWER | Author confirms campaign/product lineage and either corrects the metadata or supplies the missing primary product; then update the dataset entry. |
| 986-km NDFF QoT | Mentioned in table `340` and description `364`; citation `YangOFC2023`. | No corresponding files, record counts, timestamp coverage, sizes, exact field dictionary, or Croissant record in the current checkout. | MATERIAL_FOR_REVIEWER | Identify the external release and provide a concise source/count/format/access entry, or remove the impression that it is part of this release. |
| Urban fibre sensing | Table `341`; physical description `368-374` gives route lengths, four weeks, MAT/CSV, BER/Q/OSNR and Stokes fields. | No actual MAT/CSV files in the current checkout; no record/size/timestamp/missing-value/access metadata is locally auditable. | MATERIAL_FOR_REVIEWER | Link the actual release and add its authoritative record/format/source metadata; do not invent counts. |
| Practical wireless access telemetry | Table `342`; physical testbed description `377-381`; primary file `semantic_case_v6/data/wireless_real_30s.csv`; W1A: 2,849 x 46, 2024-10-18 20:21:30--2024-10-19 20:21:00, zero missing cells and duplicate timestamps. | The file is nominally 30 s but has 2,821 x 30-s, 23 x 60-s, and 4 x 90-s intervals; raw traffic/signal/inactivity units and formal release licence are not recoverable. | MATERIAL_FOR_REVIEWER | Report nominal plus observed interval distribution, confirm units/definitions, and state repository terms without assigning an SPDX licence unless confirmed. |
| Constructed fusion benchmark | Construction and 2,848 one-step samples described at `JOCN_Telemetry.tex:276`; implementation `run_e1_e2.py:180-210` and `644-677`. | The 1.08-MB CSV named in table `343` is not present in the current checkout; the artifact is reconstructable from code, but the positional mapping is not a measured paired dataset. | MATERIAL_FOR_REVIEWER | Identify the released derived file or describe it as code-reconstructable; retain the explicit constructed-benchmark boundary. |
| Synthetic GNPy artifact | Method/results at `JOCN_Telemetry.tex:463-494`; audit artifacts in `MajorRevision/E4_gnpy_audit/`; Croissant describes `unique_configurations.csv`. | No version-compatible original GNPy environment, complete raw artifact release in the current checkout, or independent numerical replay; warnings and duplicate executions are material. | MATERIAL_FOR_REVIEWER | Keep the artifact-audit claim bounded; provide the original environment only if available, otherwise do not imply independently reproduced numerical values. |
| Final W4C synthetic wireless DT | Method and counts at `JOCN_Telemetry.tex:497-560`; authoritative data/evidence is outside the manuscript checkout under `/home/ubuntu/Desktop/LLM Driven wireless environment generation/W4C_THREE_RAT_SWEEP/`; W4E closes the wireless line. | The manuscript row has no public release path, total size, or formal licence assertion for this final dataset. | MATERIAL_FOR_REVIEWER | Release or identify the final W4C artifact bundle and give a path/version/terms entry; do not alter frozen results. |
| Semantic utility/privacy result datasets | Croissant lists per-seed utility/privacy CSVs; code and result files are in `MajorRevision/E1_semantic_utility/` and `E2_privacy/`. | The report does not clearly distinguish derived result tables from raw datasets in the summary table, and the source snapshot/date conflict propagates to E1/E2 provenance. | MINOR to MATERIAL depending on release use | State that these are derived evaluation artifacts and freeze their exact source/data lineage. |

The metadata table therefore partially addresses R1, but it is not yet a
complete reviewer-ready data dictionary. The missing fields are mostly
author-confirmation or release-packaging tasks, not new computational
experiments.

## 5. Cross-domain definition and fusion claim audit

The current manuscript contains the correct core boundary. At
`JOCN_Telemetry.tex:95`, independently acquired datasets and a constructed
interoperability benchmark are distinguished. At `276`, the implementation is
described as positional sequence mapping with no timestamp equality. At
`326`, different campaign dates and sampling rates are acknowledged. At
`379`, the wireless signal is explicitly stated not to be converted from or
synchronised to either optical field link.

The implementation confirms this interpretation:

- `MajorRevision/run_e1_e2.py:180-210` reads separate optical and wireless
  files and maps ordered records using `np.round(np.linspace(...))`.
- The wireless range is 2024-10-18--19 and the current optical range is
  2025-12-22--2026-01-24; W1A found zero timestamp intersection.
- `run_e1_e2.py:644-663` creates rule-derived optical/wireless/service labels,
  then shifts them one record.

**Status:** the constructed-interoperability claim is supported, but the
active optical date/sampling conflict remains a material metadata defect.
There is no evidence for contemporaneous measurement, optical-to-wireless
signal conversion, physical cross-domain causality, or observed service-
failure ground truth.

The current E1 code also does not establish an incremental fusion gain. The
available methods include `OpticalOnly`, `WirelessSemanticOnly_V3`, and
`RawWirelessPlusOptical` at `run_e1_e2.py:708-719`, but there is no matched
`RawWirelessOnly` representation. `W0` therefore correctly identified a
fusion-ablation gap. The active manuscript does not currently claim that
fusion improves prediction; it says the constructed benchmark tests whether
representations remain useful. That narrower claim is defensible. A matched
wireless-only/optical-only/fused ablation is needed only if the manuscript is
expanded to claim an incremental fusion benefit.

## 6. Semantic leakage audit

### 6.1 Conventional leakage control

**Classification: `PASS_LEAKAGE_CONTROLLED`.** This status is distinct from
label validity and physical-ground-truth validity.

| Operation | Evidence | Audit result |
|---|---|---|
| Chronological split and purge | `run_e1_e2.py:213-224`; `E1_semantic_utility/temporal_split.csv` | 60/20/20 post-shift split; 1,698/560/570 evaluated rows; ten records purged before each boundary. |
| Active-RAT thresholds | `run_e1_e2.py:227-235` | 25th-percentile thresholds fit on training rows only. |
| Min-max semantic scores | `run_e1_e2.py:236-255` | Training-period min/max values only, then applied and clipped. |
| Optical risk thresholds | `run_e1_e2.py:642-646`; `E1_semantic_utility/experiment_config.json` | Q-factor/BER thresholds fit on training target positions only. |
| Encoder/decoder scaling and training | `run_e1_e2.py:404-443` | Input/target `StandardScaler` objects fit on train; encoder trained on train and selected on validation. |
| PCA/random projection | `run_e1_e2.py:701-706` | Fit on training rows only. |
| Downstream classifier | `run_e1_e2.py:461-497` | Scaling/classifier are inside a train-fitted pipeline. |
| Privacy attacker and label encoder | `run_e1_e2.py:500-556` | Attacker scaling and `LabelEncoder` fit on training labels/features only. |
| Rolling features | `run_e1_e2.py:152-155` | Five-record, backward-looking rolling operations; ten-record purge covers the record window. |
| Missing values | `run_e1_e2.py:123-127` | `fillna(0)` is applied before splitting, but W1A found zero missing CSV cells, so it has no effect on these data. Future missing data would need train-fitted imputation. |

The remaining temporal caveat is that the purge is a record count, not a
fixed elapsed-time gap, because the wireless file contains 60-s and 90-s
intervals. This does not create a conventional future-value leak in the
current backward-looking window, but it should be documented accurately.

### 6.2 Label endogeneity is not split leakage

`run_e1_e2.py:647-661` defines wireless risk from congestion, stability, and
access-diversity scores; optical risk from optical Q/BER thresholds; and the
service/degradation labels as logical combinations. The downstream feature
sets include those semantic targets or reconstructions and the optical
aggregates. The one-step shift at `662-666` avoids an exact same-row copied
label, but it does not make the target independently observed.

This is best described as a next-record recoverability test over constructed
rules, not validation against field service failures. The current manuscript
partially states this at `276`; an explicit endogeneity caveat is still
needed if the utility results remain prominent.

## 7. Utility and fusion-ablation audit

The current results are real and reproducible as a representation comparison:
ten seeds, a common temporal split, and multiple representations are in
`MajorRevision/E1_semantic_utility/utility_results_per_seed.csv` and
`utility_results_summary.csv`. The active primary results are at
`JOCN_Telemetry.tex:295-320`.

What is supported:

- V3 has similar binary utility to V1 under the constructed target;
- raw features perform best on the imbalanced four-class task;
- optical-only and wireless-semantic-only results exist;
- the reported results are not evidence of a universal fusion improvement.

What is not supported:

- an incremental contribution of the wireless domain relative to optical
  only, because matched `WirelessOnlyRaw` is absent;
- a physical complementarity or causal synergy claim;
- a claim that the positional pairing improves over a no-pairing control.

**Fusion ablation status:** `GAP_FOR_INCREMENTAL_FUSION_GAIN; CURRENT_NARROW
CLAIM_DEFENSIBLE`. No new experiment is strictly required unless the paper
uses an explicit “fusion improves prediction” claim.

## 8. Label and target validity audit

| Target | Actual construction | Current wording | Status |
|---|---|---|---|
| Binary service risk | Optical risk OR wireless risk; one-step shifted | “Rule-derived benchmark labels rather than field-observed service failures” at `JOCN_Telemetry.tex:276` | Partially explicit; endogeneity should be stated directly. |
| Four-class degradation source | Neither, wireless-only, optical-only, or both from the same two rules | Same line `276` | Appropriate only as a constructed source-of-rule label; not physical diagnosis ground truth. |
| Congestion risk | Fixed sigmoid of min-max load, inactivity, fluctuation, stability, and diversity at `run_e1_e2.py:262-269` | Semantic target at `258-264` | Deterministic engineering score, not observed congestion ground truth. |
| Dominant CPE/RAT privacy targets | `idxmax` over derived traffic aggregates at `run_e1_e2.py:157-176` | Largest aggregate contribution at `JOCN_Telemetry.tex:283` | Correct, but dominant RAT is highly imbalanced. |

The labels are not invalid for a benchmark, but the strongest defensible
claim is recoverability of specified constructed targets under a constructed
sequence benchmark. “Prediction of observed service failure” would be
overstated without independent annotations.

## 9. Privacy claim audit

The current implementation and wording are substantially aligned.

- V1/V2/V3 definitions and training noise are described at
  `JOCN_Telemetry.tex:252-266` and implemented at
  `run_e1_e2.py:679-741`.
- Four attacker families are implemented at `run_e1_e2.py:500-525`.
- Ten seeds, raw/PCA/random-projection/majority/stratified-random baselines,
  and CPE/RAT targets are present in `E2_privacy/`.
- Dominant RAT is visibly diagnostic only because the test set contains 559
  Wi-Fi and 11 LiFi records, with no 5G record; this is stated at
  `JOCN_Telemetry.tex:283`.
- The strongest observed CPE attacker results are reported in the table at
  `JOCN_Telemetry.tex:297-317`; the text at `320` explicitly rejects formal
  privacy and universal superiority.

The strongest defensible wording is **privacy-aware by design/evaluation,
with attacker-dependent empirical leakage reduction under the tested
representations and attackers**. It is not differential privacy, formal
privacy preservation, an information-theoretic guarantee, or a guarantee
against unseen attackers. V3 is not uniformly less leaky than V2 for every
attacker, and PCA/random projection can have lower observed leakage with
different utility.

**Privacy claim status:** `CLOSED_WITH_EXPLICIT_LIMITATIONS` for the wording
currently used; not evidence for a formal privacy claim.

## 10. LLM / multi-agent evaluation audit

The available evidence must be separated into two claims.

### A. Generated-simulator/data correctness

W4B/W4C/W4E strongly support the final wireless implementation and its
bounded dataset: 5G-LENA NR, native 802.11ax, equation-driven LOS LiFi/OWC,
independent LiFi checks, integrated mapping, fixed-seed repeatability, and
48-run completion. This is frozen as `WIRELESS_STATUS=FROZEN_CLOSED`.

### B. Advantage of the LLM/multi-agent architecture

The observable GNPy evidence in `MajorRevision/E3_llm_baseline/` and
`E4_gnpy_audit/` supports only:

- a deterministic enumerator generated the 6,144 expected keys in
  approximately 0.0063 s with no LLM/API call;
- the published artifact contains 8,192 executions and 6,144 unique keys,
  with 25% duplicate executions and precision/recall 1.0 against the key set;
- LLM model/provider/version, prompts, tool schemas, API calls, token counts,
  cost, latency, retry logs, human interventions, and repeated LLM trials are
  not available.

The current manuscript is honest about this at `JOCN_Telemetry.tex:434-440`
and `494`, and the W2 response says the same at
`W2_wireless_ns3_reviewer_response.md:20-26`. No evidence supports lower cost,
lower latency, higher correctness, or necessity of the LLM relative to a
deterministic workflow.

**LLM-framework evaluation status:** `PARTIALLY_CLOSED`; the feasibility claim
is supported, but a comparative LLM-performance claim remains unsupported.

## 11. Synthetic-data correctness by domain

### Wireless

**`CLOSED / FROZEN`.** W4E is authoritative. The current manuscript uses the
final W4C backend and counts at `JOCN_Telemetry.tex:497-560`, and no legacy
LTE/EPC/802.11n/CSMA-surrogate result remains on the active final claim path.
The final evidence is not physical-testbed calibration.

### GNPy optical synthetic artifact

**`PARTIALLY_CLOSED`.** The manuscript correctly reports:

- 8,192 execution records but 6,144 unique configurations;
- 6,120 `ok` and 24 no-signal unique configurations;
- warnings in the published outputs;
- 96/96 independent preparations blocked at equipment-schema validation in
  GNPy 2.14.2 and the same compatibility failure in GNPy 2.13.0;
- no pinned original working commit/container.

Evidence: `JOCN_Telemetry.tex:477-494`,
`MajorRevision/E4_gnpy_audit/README.md`,
`independent_reproduction_summary.csv`, and `provenance.json`.

Thus the manuscript can claim artifact coverage, uniqueness auditing, and
warning disclosure. It cannot claim independent numerical reproduction of the
GNPy values. If R3C4 refers to all generated data, the wireless part is closed
but the GNPy part remains partial.

## 12. Terminology and claim-consistency audit

The active synthetic wireless terminology is correct:

- `ns-3` and `ns-3.44` at `JOCN_Telemetry.tex:430`, `500-520`;
- 5G NR via CTTC 5G-LENA for W4C;
- Wi-Fi 802.11ax / Wi-Fi 6;
- equation-driven LOS LiFi/OWC with a stock packet-access abstraction.

Legacy LTE/EPC, 802.11n, and CSMA-surrogate wording remains only inside the
excluded `comment` block at `JOCN_Telemetry.tex:563-570`, where it is labelled
the preserved legacy/development use case. It is not part of the active final
synthetic claim path.

The active text does not claim contemporaneous optical-wireless collection,
physical-testbed calibration, universal RAT ranking, terminal packet loss, or
formal privacy. The material terminology issue is the optical sampling/date
conflict, not the wireless terminology.

## 13. Abstract / Introduction / Conclusion cross-check

| Location | Major active claim | Evidence | Classification |
|---|---|---|---|
| Abstract `JOCN_Telemetry.tex:72` | Practical and generated data are complementary; campaigns are independent; semantic and LLM results are bounded; GNPy has 8,192 executions and 6,144 unique configurations. | E1/E2, E3/E4 artifacts, W1A/W4C reports. | SUPPORTED, subject to optical metadata correction. |
| Introduction `95-97` | Cross-domain means common repository/representation plus a constructed interoperability benchmark; contributions include practical data, semantic evaluation, LLM DT interface, and audits. | Current code, E1/E2, E3/E4, W4C/W4E. | SUPPORTED and appropriately scoped. |
| Method `276` | Positional sequence mapping, no timestamp equality, rule-derived labels, one-step target. | `run_e1_e2.py:180-210`, `644-666`. | SUPPORTED, but label endogeneity should be stated more directly. |
| Method/results `326`, `339`, `362-364` | Dataset dates and sampling metadata. | W1A primary CSV contradicts the active optical date/sampling text. | OVERSTATED/CONFLICTING; P0 factual correction. |
| LLM method/results `438-494` | Deterministic enumeration and GNPy artifact audit; no LLM superiority or independent GNPy numerical replay claim. | E3/E4 artifacts. | SUPPORTED. |
| Wireless results `497-560` | Final W4C synthetic three-RAT dataset and bounded correctness/reproducibility evidence. | W4B/W4C/W4E. | SUPPORTED; wireless frozen. |
| Conclusion `572-574` | Constructed benchmark, bounded semantic/privacy wording, LLM feasibility, GNPy limitations, final W4C evidence, and future work. | Current artifacts and reports. | SUPPORTED with the same optical metadata and label-endogeneity caveats. |

The high-level contribution hierarchy is therefore coherent. The abstract,
introduction, and conclusion do not require broad rewriting; only targeted
fact/claim-boundary corrections are needed.

## 14. Reviewer-response quality audit

The current W2 response is strong for the selected wireless items:

- R3C4 wireless section acknowledges that successful execution alone is not
  sufficient and reports independent equation checks, mapping, repeatability,
  and W4C counts at `W2_wireless_ns3_reviewer_response.md:3-18`.
- R3C3 simulation-side response separates simulator validation from LLM
  advantage and does not invent unavailable history at `20-26`.
- R3C10 response uses final three-RAT terminology at `28-36`.
- R1 synthetic-wireless metadata response is at `38-46`.

However, no complete formal response for all 31 comments is present in the
current `MajorRevision/` directory. `06_审稿意见处理状态.md` is an internal
status ledger, not a point-by-point response. Consequently, for R1C1-R1C3,
most R2 comments, and R3C1-R3C2/R3C5-R3C12, the current “response location”
is either the ledger or missing. A submission package needs one response
document with each comment exactly once, manuscript locations, actual evidence,
and remaining limitations.

The R3C4 numbering conflict must be fixed in that response: either verify the
original identifier and combine both GNPy and wireless evidence under it, or
use the original letter’s separate identifiers. The present response cannot
silently treat the wireless W4E closure as closure of the GNPy replay gap.

## 15. Complete reviewer-comment closure matrix

The matrix uses the 31 comments recovered from the local status ledger. Each
comment appears exactly once.

| Reviewer | Comment | Core concern | Manuscript evidence | Response evidence | Status | Remaining action | New experiment? |
|---|---|---|---|---|---|---|---|
| R1 | R1C1 | Cross-domain meaning is unclear; campaigns are independent. | `JOCN_Telemetry.tex:95`, `276`, `326`, `379`; constructed positional benchmark and no synchronization claim. | `06_审稿意见处理状态.md:9`; no complete formal response. | PARTIALLY_CLOSED | Resolve optical date/sampling conflict and preserve constructed-benchmark wording; verify against original letter. | No, unless a different primary optical product is supplied. |
| R1 | R1C2 | LLM model/calls/failures/cost/latency/human intervention and script baseline. | `JOCN_Telemetry.tex:438-440`, Table `442-459`; missing LLM records explicitly disclosed; deterministic 6,144-key enumerator. | `06:10`, `03_E3_LLM基线实验结果.md`; no complete point-by-point response. | PARTIALLY_CLOSED | Supply archived LLM logs if they exist; otherwise retain “not reported” and bounded feasibility/no-superiority claim in the formal response. | No for bounded claim; a true LLM comparison would require new evidence. |
| R1 | R1C3 | Dataset summary metadata and machine-readable metadata. | Table `328-347`; `MajorRevision/croissant_metadata.json`; only some processed files are described. | `06:11`; W2 synthetic-wireless item `38-46`. | PARTIALLY_CLOSED | Add/confirm source paths, units, observed time coverage, missing-value policy, external dataset entries, and formal terms; resolve Voyager lineage. | No; author/release metadata required. |
| R2 | R2C1 | Main contribution and contribution hierarchy are unclear. | Abstract `72`; Introduction `95-97`; Conclusion `572-574`. | `06:17`; no complete formal response. | CLOSED | None for current bounded hierarchy. | No. |
| R2 | R2C2 | Related Work structure is repetitive and transitions are unclear. | `JOCN_Telemetry.tex:125-152` separates data/telemetry, semantic privacy, and DT/LLM work. | `06:18`. | CLOSED | None. | No. |
| R2 | R2C3 | Existing-work limitations are repeated. | Related Work `132`, `146-152` concentrates limitations by subsection; current Introduction is shorter. | `06:19`. | CLOSED | None. | No. |
| R2 | R2C4 | Related Work overlaps with Introduction. | Introduction `95-107` states problem/contributions; Related Work `125-152` provides evidence/context. | `06:20`. | CLOSED | None. | No. |
| R2 | R2C5 | How the orchestrator coordinates Fig. 1 components is unclear. | `JOCN_Telemetry.tex:174-180`, `426-434`; Fig. 1 is a scope map and Fig. 6 is the evaluated sequence. | `06:21`. | CLOSED | None. | No. |
| R2 | R2C6 | Autonomous closed-loop wording lacked support/citations. | `JOCN_Telemetry.tex:146-152`, `236`, `430-434`; cited prior work and explicit non-evaluation of closed-loop enforcement. | `06:22`. | CLOSED | None. | No. |
| R2 | R2C7 | Scalability was claimed without evaluation. | `JOCN_Telemetry.tex:224`, `434`, `494`; no scalability result is claimed for the current work. | `06:23`. | CLOSED | None. | No. |
| R2 | R2C8 | IV-A was verbose; inheritance and prospective functions were unclear. | `JOCN_Telemetry.tex:190`, `213-244`; earlier platform is identified and prospective AI/controller functions are bounded. | `06:24`. | CLOSED | None. | No. |
| R2 | R2C9 | V1’s eight semantic features lacked raw-source, formula, and rationale detail. | `JOCN_Telemetry.tex:258-266` gives 12 inputs and formulas for D/S/C, but not a full z1-z8 raw-column/formula table. Exact implementation is `run_e1_e2.py:123-176`, `227-276`, `674-677`. | `06:25`; no dedicated formal response. | PARTIALLY_CLOSED | Add a compact z1-z8 table with raw columns, window, train-only scaling, units or “unit not recorded,” and engineering rationale; state that scores are deterministic features. | No. |
| R2 | R2C10 | Why V3 is called privacy-aware. | `JOCN_Telemetry.tex:252`, `283`, `295`, `320`; E2 has four attackers, baselines, ten seeds, and no formal guarantee. | `06:26`; no complete formal response. | CLOSED | Keep attacker-dependent and non-formal wording; do not claim V3 is uniformly best. | No. |
| R2 | R2C11 | Wireless signal source and relationship to optical link. | `JOCN_Telemetry.tex:379-381`; wireless campaign is independent and not optical-converted or synchronized. | `06:27`; W2 `38-46` also separates measured and synthetic wireless. | CLOSED | None for the current factual boundary. | No. |
| R2 | R2C12 | Orchestrator location and arrow semantics in the architecture figure. | `JOCN_Telemetry.tex:180`, `434`; arrows are shared orchestration-layer access, not local control. | `06:28`. | CLOSED | None. | No. |
| R2 | R2C13 | Fig. 1/Fig. 6 repetition and unreported AI-engine/controller results. | Captions `166`, `206`; method `178`, `236`, `428-434` distinguish scope/context from evaluated functions. | `06:29`. | CLOSED | None. | No. |
| R2 | R2C14 | Whether five components are really agents, why needed, and overhead. | `JOCN_Telemetry.tex:432-434` defines orchestrated invocation roles, rationale, deterministic replaceability, and unmeasured overhead. | `06:30`; no complete formal response. | PARTIALLY_CLOSED | Formal response should state qualitative engineering rationale and explicitly mark communication overhead/unassessed autonomy as limitations. | No for current claim; overhead experiment only for a stronger efficiency claim. |
| R2 | R2C15 | Reflection Agent text contrast is insufficient. | Current asset `Figures/architecture_LLM_revision.png`; status ledger `06:31`. | `06:31`; no complete formal response. | CLOSED | None. | No. |
| R2 | R2C16 | Fig. 7 resolution is insufficient and counts were confusing. | Current asset `Figures/usecase1_revision.png`; caption `JOCN_Telemetry.tex:470` distinguishes executions, unique, valid, and no-signal counts. | `06:32`; no complete formal response. | CLOSED | None. | No. |
| R3 | R3C1 | Semantic-fusion experiment is not reproducible and random split leaks. | `JOCN_Telemetry.tex:276`, `281-283`; `run_e1_e2.py:213-224`, `227-276`, `404-443`, `461-556`; train-only preprocessing and chronological purge are observed. | `06:38`; E1/E2 READMEs and configs. | PARTIALLY_CLOSED | Freeze/confirm exact optical source lineage; add full z1-z8 mapping and explicit label-endogeneity boundary. | No for leakage; rerun only if the author supplies a different optical product. |
| R3 | R3C2 | Original Table 1 did not prove privacy improvement. | Table `297-317`; text `295-320`; E2 includes raw/PCA/random/majority baselines, four attackers, ten seeds, and imbalance warning. | `06:39`; no complete formal response. | CLOSED | Retain empirical attacker-dependent wording and no formal guarantee. | No. |
| R3 | R3C3 | LLM framework is insufficiently evaluated. | `JOCN_Telemetry.tex:426-440`, `463-494`; deterministic baseline and artifact audit are present, unavailable LLM histories are disclosed. | W2 `20-26`; `06:40`. | PARTIALLY_CLOSED | In formal response distinguish generated-data correctness from LLM-vs-deterministic superiority; state missing logs without inventing them. | No for bounded feasibility; new LLM trials only for superiority claims. |
| R3 | R3C4 | Generated data lack independent correctness validation. | Wireless: `JOCN_Telemetry.tex:517-541`, W4E, W4C; GNPy: `481-494`, E4 audit. Wireless validation is closed; GNPy numerical replay is blocked. | W2 `3-18` covers wireless; `06:41` covers GNPy; identifier conflict requires original-letter check. | PARTIALLY_CLOSED | In the formal response address both tracks once under the verified identifier; claim GNPy artifact coverage/warnings, not independent numerical reproduction, unless original environment is supplied. | No for current bounded claims; GNPy rerun required only for numerical-reproduction claim. |
| R3 | R3C5 | Abstract must distinguish implemented/evaluated/demonstrated/proposed. | Abstract `72`; framework boundaries `178`, `236`, `420-440`; prospective components are identified. | `06:42`; no complete formal response. | CLOSED | None. | No. |
| R3 | R3C6 | Sections III and IV-A overlap. | Current Section organization `172-182` versus `184-246`; scope map and implementation detail are separated. | `06:43`. | CLOSED | None. | No. |
| R3 | R3C7 | AC/DC power details are unnecessary or unsupported. | No active AC/DC discussion remains; status ledger `06:44`. | `06:44`; no complete formal response. | CLOSED | None. | No. |
| R3 | R3C8 | $-5$ dBm was presented as an optimal setting. | `JOCN_Telemetry.tex:362-364` calls it the campaign operating point and explicitly makes no optimality claim. | `06:45`. | CLOSED | None. | No. |
| R3 | R3C9 | British and American spelling are mixed. | Active text uses British forms such as “organised,” “generalisation,” “optimisation,” and “fibre”; old commented text is excluded. | `06:46`. | CLOSED | None. | No. |
| R3 | R3C10 | ns-3 and title capitalization/terminology. | Active text consistently uses `ns-3`; final W4C terms appear at `497-560`; legacy terms are excluded/comment-labelled. | `06:47`; W2 `28-36` for final wireless terminology. | CLOSED | None for active claims. | No. |
| R3 | R3C11 | Placeholder DOI appears on the first page. | DOI template is commented at `JOCN_Telemetry.tex:64-65`. | `06:48`; no complete formal response. | CLOSED | None. | No. |
| R3 | R3C12 | Three spelling/grammar errors. | Status ledger records corrections at `06:49`; no corresponding active malformed phrases were found in the current text. | `06:49`; no complete formal response. | CLOSED | None. | No. |

### Closure totals

```text
TOTAL_COMMENTS=31
CLOSED=23
PARTIALLY_CLOSED=8
OPEN=0
```

## 16. Prioritized remaining work

### P0 — MUST FIX BEFORE RESUBMISSION

| Item | Comments | Exact problem | Minimum correction | New experiment? | Burden |
|---|---|---|---|---|---|
| P0-1 Optical source/date/sampling fact resolution | R1C1, R1C3, R3C1, R3C5 | Current primary Voyager values conflict with active 2023/10-s/15-min wording; lineage is missing. | Obtain author confirmation or missing primary product; update only the affected metadata/method wording and freeze the selected source. If a different product is intended, rerun affected E1/E2. | Conditional only; none if current file is confirmed. | NONE for confirmation; MODERATE if a different product requires rerun. |
| P0-2 Complete semantic reproducibility disclosure | R2C9, R3C1 | Current body gives partial formulas but not a reviewer-ready z1-z8 raw-column/formula/window/units table. | Add a compact mapping table or appendix entry; mark raw units as unknown where not documented; retain train-only thresholds/scalers. | No. | NONE. |
| P0-3 Make target endogeneity and fusion boundary explicit | R1C1, R3C1, R3C2 | Labels are rule-derived from quantities also present/reconstructed in features; no matched raw-wireless-only fusion ablation exists. | State that utility is next-record recoverability on a constructed benchmark; do not claim physical service-failure prediction or incremental fusion gain. | No for the bounded claim. | NONE. |
| P0-4 Assemble a complete point-by-point response | All partially closed items; especially R1C2/R1C3/R2C9/R2C14/R3C3/R3C4 | Current `W2_wireless_ns3_reviewer_response.md` is not a full response, and R3C4 numbering conflicts between the ledger and response. | Create one response document containing all 31 comments exactly once, manuscript locations, evidence, limitations, and a verified R3C4 identifier. | No. | NONE. |
| P0-5 Complete release metadata for claimed datasets | R1C3, R2C11, R3C3/R3C4 | Current checkout lacks several datasets and final W4C public path/terms; no formal SPDX terms confirmed. | Identify actual external files/releases and licence terms; do not invent counts, sizes, units, or legal terms. | No. | NONE. |

### P1 — STRONGLY RECOMMENDED

| Item | Comments | Scientific purpose | Minimum action | New experiment? | Burden |
|---|---|---|---|---|---|
| P1-1 Matched fusion ablation | R1C1, R3C1 | Test incremental Wireless-only vs Optical-only vs fused utility under the same split/model. | Run only if the manuscript retains an explicit fusion-gain claim; otherwise retain the current bounded construction claim. | Yes, if stronger claim is desired. | MODERATE. |
| P1-2 Original LLM provenance bundle | R1C2, R3C3, R2C14 | Evaluate LLM architecture rather than only output correctness. | Release model/provider/version, prompts, tool schema, calls, retries, cost/latency, interventions if they exist; otherwise keep “not reported.” | No if unavailable; new trials needed for comparative superiority. | NONE for disclosure; HEAVY for new study. |
| P1-3 GNPy reproducibility environment | R3C4 | Allow independent numerical replay of the optical synthetic artifact. | Supply original working commit/container or remove any implication of independent numerical reproduction. | Yes only if numerical reproduction is retained. | MODERATE to HEAVY. |
| P1-4 Extend machine-readable metadata | R1C3 | Make all practical and derived datasets discoverable with source/format/count/units/terms. | Extend Croissant or an accompanying data dictionary after author confirmation. | No. | LIGHT. |

### P2 — OPTIONAL / NICE TO HAVE

| Item | Scientific purpose | New experiment? | Burden |
|---|---|---|---|
| P2-1 Multi-trial LLM/no-reflection/agent comparison | Quantify whether the multi-agent design improves effort or correctness over scripts. | Yes. | HEAVY. |
| P2-2 Confidence calibration for `semantic_confidence` | Test whether the heuristic `1 - normalized fluctuation` predicts correctness or uncertainty. | Yes. | LIGHT to MODERATE. |
| P2-3 Broader privacy attacker/OOD study | Test robustness beyond the four current attackers and one constructed split. | Yes. | MODERATE. |
| P2-4 Larger cross-domain or simultaneous campaign | Establish physical temporal/causal cross-domain validity. | Yes, and requires new measured data. | HEAVY. |

## 17. Minimum defensible claim boundary after P0 closure

After the P0 wording/metadata/response corrections, the paper can
defensibly claim:

- independently acquired practical optical, sensing, and wireless datasets
  organised through a common framework;
- a constructed optical-wireless interoperability benchmark with explicit
  non-synchronization and rule-derived labels;
- leakage-controlled semantic representation experiments with an empirical,
  attacker-dependent privacy/utility trade-off;
- a bounded LLM/DT feasibility demonstration with a deterministic
  configuration baseline;
- final W4C wireless synthetic-data correctness and reproducibility under the
  declared ns-3.44/5G-LENA/802.11ax/equation-driven LiFi assumptions;
- GNPy artifact coverage and warning/uniqueness auditing, but not independent
  numerical reproduction unless the missing environment is supplied.

The paper cannot defensibly claim, without new evidence:

- contemporaneous optical-wireless measurement or physical causal coupling;
- physical service-failure ground truth for the constructed labels;
- incremental cross-domain fusion benefit from the current E1 ablations;
- formal privacy preservation or universal V3 superiority;
- LLM efficiency/cost/correctness superiority over deterministic scripts;
- independently reproduced GNPy numerical values from the currently released
  public inputs;
- a formal licence, physical units, or exact source lineage that are not
  documented by the authors.

## 18. Final audit status

```text
W5B_VERDICT=TARGETED_CLOSURE_REQUIRED_BEFORE_RESUBMISSION
TOTAL_REVIEWER_COMMENTS=31
CLOSED_COMMENTS=23
PARTIALLY_CLOSED_COMMENTS=8
OPEN_COMMENTS=0
P0_ITEMS=5
P1_ITEMS=4
P2_ITEMS=4
CROSS_DOMAIN_CLAIM_STATUS=CONSTRUCTED_INTEROPERABILITY_BOUNDARY_SUPPORTED; OPTICAL_METADATA_CONFLICT_REMAINS
SEMANTIC_LEAKAGE_STATUS=PASS_LEAKAGE_CONTROLLED; LABEL_ENDOGENEITY_IS_SEPARATE
FUSION_ABLATION_STATUS=GAP_FOR_INCREMENTAL_GAIN; CURRENT_NARROW_CLAIM_DEFENSIBLE
LABEL_VALIDITY_STATUS=PARTIAL_RULE_DERIVED_NOT_FIELD_GROUND_TRUTH; ENDOGENEITY_NEEDS_EXPLICIT_WORDING
PRIVACY_CLAIM_STATUS=CLOSED_FOR_PRIVACY_AWARE_EMPIRICAL_TRADEOFF; NO_FORMAL_GUARANTEE
LLM_FRAMEWORK_EVALUATION_STATUS=PARTIALLY_CLOSED_FEASIBILITY_ONLY; NO_LLM_SUPERIORITY_EVIDENCE
PRACTICAL_DATASET_METADATA_STATUS=PARTIAL_AUTHOR_CONFIRMATION_AND_RELEASE_METADATA_REQUIRED
SYNTHETIC_OPTICAL_VALIDATION_STATUS=PARTIAL_GNPY_ARTIFACT_AUDIT_WITHOUT_INDEPENDENT_NUMERICAL_REPLAY
WIRELESS_STATUS=FROZEN_CLOSED
ABSTRACT_INTRO_CONCLUSION_STATUS=MOSTLY_SUPPORTED; OPTICAL_METADATA_AND_LABEL_BOUNDARY_REQUIRE_TARGETED_CORRECTION
NEW_EXPERIMENTS_STRICTLY_REQUIRED=NO_FOR_CURRENT_BOUNDED_CLAIMS; CONDITIONAL_FOR_DIFFERENT_OPTICAL_SOURCE_OR_STRONGER_FUSION_LLM_GNPY_CLAIMS
READY_FOR_W5C_TARGETED_CLOSURE=YES
```
