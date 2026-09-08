# Complete point-by-point reviewer response for W5C-A

## Important source note

The local workspace does not contain the original decision letter or full
reviewer PDFs. The comment text below is the normalized English rendering of
the 31 entries in `MajorRevision/06_审稿意见处理状态.md:5-49`. The authors must
verify the wording and identifiers against the original letter before
submission. In particular, the local ledger uses R3C4 for the GNPy
correctness issue, while the earlier wireless response uses R3C4 for ns-3
correctness. The response below deliberately reports both evidence tracks
without silently changing the original identifier.

No new experiment was run in W5C-A. References to results point to existing
artifacts and the current manuscript.

## Reviewer 1

### R1C1 — The cross-domain meaning is unclear because the three datasets came from independent campaigns.

**Response.** We agree that the practical datasets must not be presented as a
single contemporaneous optical--wireless measurement. We now define
``cross-domain'' in two bounded senses: common repository/metadata and a
constructed sequence-aligned interoperability benchmark. The optical and
wireless files are read separately and their ordered records are mapped by
relative sequence position; no timestamp equality, optical-to-wireless signal
conversion, physical causal relation, or simultaneous campaign is claimed.
The current Voyager file's timestamp coverage and interval pattern are now
reported as file-level observations rather than silently identified with the
historical campaign dates.

**Exact manuscript change/location.** Abstract; Introduction; `sec:SemanticModules`
benchmark paragraph; `tab:dataset_summary`; practical-data subsection. The
implementation is `MajorRevision/run_e1_e2.py:180-210`.

**Evidence/result.** W1A found zero timestamp intersection between the current
optical and wireless files and verified that mapping uses
`round(linspace(...))`; the benchmark has 2,848 one-step samples.

**Limitation.** The physical Voyager product identity/date and the relation to
any earlier 10-s/15-minute product are not established by the current files.
`W5C_author_confirmation_required.md` records the required confirmation.

**Status.** `BLOCKED_ON_AUTHOR_CONFIRMATION` for final provenance closure;
the scientific constructed-benchmark wording is closed.

### R1C2 — Report the LLM model, calls, failures, cost, latency, human intervention, and a script baseline.

**Response.** We added and retain a deterministic enumeration baseline for the
6,144 expected GNPy configuration keys. It enumerates the set in 0.0063 s
without an LLM/API call, while the published artifact contains 8,192
execution records and 6,144 unique configurations. The manuscript now
explicitly states that the public materials do not report the LLM model or
version, prompts, tool schema, API calls, tokens, cost, latency, retries,
failures, or human interventions. We therefore limit the claim to a bounded
LLM-driven workflow feasibility demonstration and do not claim LLM
superiority over the deterministic script.

**Exact manuscript change/location.** `JOCN_Telemetry.tex`,
`Evaluation Protocol and Reproducibility Scope`, Table~\ref{tab:llm_baseline},
and GNPy results subsection. Existing evidence is summarized in
`MajorRevision/03_E3_LLM基线实验结果.md` and
`E3_llm_baseline/observable_baseline_comparison.csv`.

**Evidence/result.** Deterministic enumeration has precision and recall 1.0
against the expected set; the published artifact has 25% duplicate execution
records. The current source contains no historical LLM trace bundle.

**Limitation.** A controlled LLM-vs-script advantage study cannot be claimed
without the missing logs or new controlled trials. The author must confirm
whether the unavailable records truly do not exist.

**Status.** `BLOCKED_ON_AUTHOR_CONFIRMATION` for historical metadata; the
bounded feasibility claim is supported.

### R1C3 — Add a dataset summary table and machine-readable metadata such as Croissant.

**Response.** We added the dataset summary table and retained
`MajorRevision/croissant_metadata.json`. The W5C matrix now separates
practical, synthetic, and derived artifacts and records supported counts,
formats, paths, and known limitations. Unknown external file paths, raw
units, formal licence terms, and unresolved optical lineage are marked rather
than fabricated.

**Exact manuscript change/location.** `tab:dataset_summary` and the practical
dataset subsection. The complete machine-readable audit is
`W5C_dataset_metadata_matrix.md`.

**Evidence/result.** The current Croissant file documents the processed
wireless/Voyager tables, E1/E2 result tables, and deduplicated GNPy audit CSV,
with recorded sizes and hashes. The final W4C row reports 48 configurations,
432 application-flow records, and 624 raw FlowMonitor rows.

**Limitation.** The current checkout does not contain the 986-km and urban
sensing primary files, a standalone constructed-fusion CSV, or the final W4C
bundle. No standard LICENSE/SPDX file is present in the checkout. Authoritative
release paths and terms must be confirmed before final submission.

**Status.** `BLOCKED_ON_AUTHOR_CONFIRMATION` for release packaging.

## Reviewer 2

### R2C1 — The main contribution and hierarchy are unclear.

**Response.** We reorganised the framing around practical datasets and
generated datasets, then describe semantic abstraction and LLM-driven DT
demonstrations as supporting evaluation interfaces. The conclusion follows
the same hierarchy: practical campaigns, constructed semantic benchmark,
bounded LLM feasibility, and final wireless correctness evidence.

**Exact manuscript change/location.** Abstract, Introduction contributions,
`sec:LLM`, and Conclusions.

**Evidence/result.** The abstract now distinguishes independently acquired
practical data, constructed benchmark evaluation, GNPy artifact auditing, and
synthetic wireless generation.

**Limitation.** The GNPy numerical replay limitation and the constructed
fusion-target limitation remain explicit.

**Status.** `CLOSED` for the current contribution hierarchy.

### R2C2 — Related Work is repetitive and transitions are unclear.

**Response.** Related Work is separated into data/telemetry, semantic privacy,
and DT/LLM generation. The transitions explain why practical telemetry is
followed by semantic abstraction and then synthetic-data generation.

**Exact manuscript change/location.** Related Work, Section II, especially
the subsections covering data availability, semantic communication/privacy,
and DT/LLM generation.

**Evidence/result.** The active text assigns a distinct purpose to each
subsection and no longer repeats the complete limitations argument in every
subsection.

**Limitation.** This is a structural/textual correction; no new experiment is
needed.

**Status.** `CLOSED`.

### R2C3 — Limitations of existing work are repeated.

**Response.** We consolidated the cross-domain data and alignment limitations
in the data/telemetry discussion and retained only the generation-specific
manual-effort limitation in the DT/LLM discussion.

**Exact manuscript change/location.** Related Work, Sections II-A and II-C.

**Evidence/result.** The active Related Work now uses one limitation-to-gap
transition per topic rather than repeating the same paragraph.

**Limitation.** No new evidence is required.

**Status.** `CLOSED`.

### R2C4 — Related Work overlaps with the Introduction.

**Response.** The Introduction states the problem, scope, contribution
hierarchy, and paper organisation. Related Work provides the prior evidence,
limitations, and positioning. The distinction is maintained in the current
section text.

**Exact manuscript change/location.** Introduction and Section II.

**Evidence/result.** Introduction `95-107` contains the contribution path;
Related Work `125-152` contains the literature-based context.

**Limitation.** No new experiment is required.

**Status.** `CLOSED`.

### R2C5 — It is unclear how the orchestrator coordinates the Fig. 1 components.

**Response.** The manuscript now identifies Fig. 1 as a scope map and explains
that the demonstrated orchestrator passes a shared structured task state
through planning, scenario expansion, DT execution, analysis, reflection,
and reporting. The AI-engine and controller blocks provide context or
prospective integration points, not unreported evaluated closed-loop
components.

**Exact manuscript change/location.** Framework overview and
`Proposed LLM-Driven Multi-Agent Digital Twin Framework`, including the Fig. 1
caption and lines describing the orchestrator-owned task state.

**Evidence/result.** The current workflow invokes the five named functional
roles and records intermediate artifacts; the text explicitly distinguishes
shared orchestration-layer arrows from direct local control.

**Limitation.** Persistent autonomous agents and communication overhead are
not claimed or measured.

**Status.** `CLOSED`.

### R2C6 — The autonomous closed-loop claim lacks citation/support.

**Response.** We added the relevant prior-work context and narrowed the paper's
own claim. The current study demonstrates request-to-artifact generation and
reflection-triggered expansion; it does not establish autonomous closed-loop
network enforcement.

**Exact manuscript change/location.** Related Work DT/LLM subsection and
`JOCN_Telemetry.tex:426-440`.

**Evidence/result.** The manuscript cites prior DT/agent studies and explicitly
states that the physical network, AI-engine, and controller blocks are not
exercised as a live closed-control loop here.

**Limitation.** No autonomous deployment or closed-loop performance claim is
made.

**Status.** `CLOSED`.

### R2C7 — Scalability is claimed without evaluation.

**Response.** We removed scalability as a demonstrated result. The framework
is described as extensible, while the current evidence is limited to the
reported configuration spaces and bounded W4C sweep.

**Exact manuscript change/location.** Framework and LLM evaluation text,
including the explicit future-work statement for larger scenario spaces.

**Evidence/result.** The available evidence covers the 6,144-key GNPy
configuration set and the W4C 48-run wireless sweep; no extrapolated scaling
curve is reported.

**Limitation.** Larger-scale execution and cost/latency scaling remain future
work.

**Status.** `CLOSED`.

### R2C8 — Section IV-A is verbose and inheritance/prospective functions are unclear.

**Response.** We compressed the inherited telemetry/storage description and
separated implemented functions from prospective forecasting, AI-engine, and
controller functions. The current paper identifies the earlier platform as
the basis and states which functions are not evaluated here.

**Exact manuscript change/location.** Practical architecture subsection and
framework overview.

**Evidence/result.** The current architecture text distinguishes implemented
collection/storage paths from contextual or prospective modules.

**Limitation.** No new implementation or evaluation is implied for those
prospective modules.

**Status.** `CLOSED`.

### R2C9 — The eight V1 semantic features lack raw sources, formulas, and rationale.

**Response.** We now give the complete z1-z8 mapping. z1 is the training-only
min--max-normalised total traffic; z2 is the weighted stability formula from
signal quality, fluctuation, and inactivity; z3 is the mean of three
training-thresholded RAT activity indicators; z4 is the stated logistic
congestion formula; z5 and z6 are training-normalised five-record rolling mean
and rolling standard deviation; z7 is the 0.7/0.3 weighted Wi-Fi/LiFi signal
quality; and z8 is training-normalised mean Wi-Fi inactivity. The exact raw
column groups are listed in the new manuscript paragraph and the W5C audit.

**Exact manuscript change/location.** `subsec:SemanticModules`, immediately
after the semantic-module architecture paragraph. Exact implementation:
`MajorRevision/run_e1_e2.py:123-176`, `227-276`, and `674-677`.

**Evidence/result.** All eight values are deterministic engineered features;
training-only thresholds/min--max ranges are used. The five-record rolling
operations are backward-looking and the ten-record purge is retained.

**Limitation.** The CSV does not record formal physical units for all raw
traffic/signal/inactivity fields; the manuscript marks units as not retained
or not recorded rather than guessing. `semantic_confidence` is a heuristic,
not probability.

**Status.** `CLOSED` for reproducibility.

### R2C10 — Why is V3 called privacy-aware?

**Response.** We define privacy-aware as a design/evaluation objective, not a
formal guarantee. V3 varies dimensionality and optional training-time input
noise, and E2 evaluates attribute inference with logistic regression, random
forest, MLP, and histogram gradient boosting against raw, V1/V2, PCA,
random-projection, majority, and stratified-random baselines over ten seeds.

**Exact manuscript change/location.** Semantic-module introduction, privacy
method/results, and Table~\ref{tab:semantic_module_results}.

**Evidence/result.** V3 reduces observed CPE attacker Macro-F1 relative to raw
telemetry in the reported setting, while PCA can leak less and retain less
utility. V3 is not uniformly the lowest-leakage representation.

**Limitation.** No differential privacy, adversarial privacy objective, or
guarantee against unseen attackers is claimed.

**Status.** `CLOSED` for the bounded empirical claim.

### R2C11 — What is the wireless signal source and how is it related to the optical link?

**Response.** The practical wireless records come from the separate
5G-CLARITY/REASON multi-access wireless testbed. They are not converted from,
carried by, or synchronized to either optical field link. The optical and
wireless files are combined only in the constructed sequence benchmark.

**Exact manuscript change/location.** Practical wireless subsection and
constructed benchmark paragraph; `build_wireless_base()` and
`build_optical_aligned()` in `run_e1_e2.py`.

**Evidence/result.** The wireless file contains 2,849 records and the optical
file is read separately; W1A found no timestamp overlap.

**Limitation.** This does not establish physical cross-domain causality or a
joint field campaign.

**Status.** `CLOSED` for the scientific boundary; release terms remain in the
metadata confirmation list.

### R2C12 — The orchestrator position and arrows in the architecture figure are unclear.

**Response.** The text now explains that the orchestrator owns shared task
state and invokes the five functional roles in sequence. The arrows below the
roles denote access to the shared orchestration layer, not direct control by
only the lower-right roles; the layout is not an execution-order diagram.

**Exact manuscript change/location.** Fig. 1/Fig. 6 captions and framework
description at `JOCN_Telemetry.tex:426-434`.

**Evidence/result.** The evaluated sequence and its retained artifacts are
shown separately from the broader scope map.

**Limitation.** The figure does not claim independent persistent subagent
schedulers.

**Status.** `CLOSED`.

### R2C13 — Fig. 1 and Fig. 6 overlap, and the AI engine/controller have no results.

**Response.** Fig. 1 is now explicitly a scope/context map; Fig. 6 is the
evaluated orchestrator sequence. AI-engine and controller blocks are labelled
as contextual/prospective and are not presented as measured results.

**Exact manuscript change/location.** Captions for Fig. 1 and Fig. 6, and the
framework paragraphs distinguishing implemented and prospective functions.

**Evidence/result.** Only the documented GNPy/ns-3 DT paths and retained
artifacts are used as evaluated workflow evidence.

**Limitation.** No unreported AI-engine/controller experiment is implied.

**Status.** `CLOSED`.

### R2C14 — Are the five components really agents, why are they needed, and what is their overhead?

**Response.** We define the five components as functional LLM-invocation roles
within an orchestrated pipeline, not independently persistent autonomous
agents. Their qualitative engineering rationale is explicit: each role has a
schema-defined transition and inspectable intermediate artifact. Deterministic
functions could replace any role. Communication overhead and autonomous
coordination overhead are not measured, so no efficiency claim is made.

**Exact manuscript change/location.** LLM framework paragraph at
`JOCN_Telemetry.tex:432-434`; response evidence in this document.

**Evidence/result.** Planner, Scenario Expansion, Results Analysis,
Reflection, and Report roles are described with their inputs/outputs and
shared task state.

**Limitation.** The role decomposition is an engineering design rationale,
not a measured proof of necessity or lower overhead.

**Status.** `CLOSED` with the overhead limitation explicit.

### R2C15 — The Reflection Agent text contrast is insufficient.

**Response.** The architecture asset was revised with darker title and
description text, and the high-resolution PNG is used by the manuscript.

**Exact manuscript change/location.** `Figures/architecture_LLM_revision.png`
and the Fig. 6/architecture reference.

**Evidence/result.** The revision asset is the current included figure.

**Limitation.** This is a figure legibility correction, not a new experiment.

**Status.** `CLOSED`.

### R2C16 — Fig. 7 resolution is insufficient and its counts are confusing.

**Response.** Fig. 7 was regenerated at higher resolution and its caption now
distinguishes execution records, unique configurations, valid records, and
no-signal records.

**Exact manuscript change/location.** `Figures/usecase1_revision.png` and
the GNPy figure caption.

**Evidence/result.** The active caption reports 8,192 executions, 6,144 unique
configurations, 6,120 valid, and 24 no-signal configurations.

**Limitation.** The counts do not imply independent numerical replay; that
limitation is reported in the GNPy subsection.

**Status.** `CLOSED`.

## Reviewer 3

### R3C1 — The semantic-fusion experiment is not reproducible and the random split leaks.

**Response.** We replaced the random-split description with a chronological
60/20/20 split and a ten-record purge. Active-RAT thresholds, min--max and
standard scalers, optical risk thresholds, encoders, PCA/random projection,
classifiers, and privacy attackers are fitted using training data only. The
complete z1-z8 mapping is now explicit. We also clarify that leakage control
does not remove label endogeneity: the one-step targets are rule-derived from
related optical/semantic quantities rather than independent field annotations.

**Exact manuscript change/location.** Semantic benchmark and testing
subsections; `MajorRevision/run_e1_e2.py:213-276`, `404-443`, `461-556`, and
`640-677`; E1/E2 configuration and temporal split artifacts.

**Evidence/result.** E1 records 1,698/560/570 evaluated samples, ten seeds,
and train-only preprocessing. The optical and wireless campaigns remain
separate and the benchmark uses positional sequence mapping.

**Limitation.** The exact optical product lineage remains unresolved. No
matched raw-wireless-only ablation exists, so no incremental fusion gain is
claimed. Author confirmation is required if a different optical product was
intended.

**Status.** `BLOCKED_ON_AUTHOR_CONFIRMATION` for source freeze; split-leakage
control is supported.

### R3C2 — The original Table 1 did not prove privacy improvement.

**Response.** E2 now reports multiple representations and baselines against
four attacker families, with ten repeated seeds and CPE Macro-F1 as the
primary metric. Dominant RAT is retained only as an imbalanced diagnostic.
The manuscript reports that PCA can expose less CPE information than V3 but
also reduces utility, and that V3 is not uniformly best.

**Exact manuscript change/location.** Privacy method/results and
Table~\ref{tab:semantic_module_results}; `MajorRevision/E2_privacy/`.

**Evidence/result.** Raw private features have strongest observed CPE
attacker Macro-F1 0.2757, V3 3D with sigma 0.05 has 0.2382, and PCA3 has
0.2174; these are attacker-dependent empirical results.

**Limitation.** No formal privacy guarantee or universal representation
ordering is claimed.

**Status.** `CLOSED` for the bounded empirical privacy claim.

### R3C3 — The LLM framework is insufficiently evaluated.

**Response.** The simulation-side evaluation now distinguishes the LLM
workflow from generated-data validation. The workflow is demonstrated with
GNPy and the final W4C three-RAT ns-3 scenario; the deterministic GNPy
enumerator provides a non-LLM baseline. W4C provides independent LiFi
equation checks, integrated flow mapping, fixed-seed repeatability, and a
48-configuration synthetic dataset. These support executable workflow and
output correctness under declared assumptions, not LLM superiority.

**Exact manuscript change/location.** LLM evaluation subsection,
`sec:ns3_wireless`, Table~\ref{tab:ns3_validation}, and Conclusions.

**Evidence/result.** W4C contains 48 configurations and 432 application-flow
records with 432/432 mapping passes; GNPy enumeration has 1.0 precision and
recall against 6,144 keys.

**Limitation.** Historical model/provider/version, prompt, token, cost,
latency, retry, and human-intervention logs are unavailable. No claim of
LLM-vs-script superiority is made.

**Status.** `CLOSED` for the bounded simulation-side feasibility claim;
historical LLM metadata remains unreported.

### R3C4 — The generated data lack independent correctness validation.

**Response.** We agree that successful execution alone cannot detect a
plausible but incorrectly configured simulator, KPI extractor, or flow
mapping. The final wireless track adds: (1) independent LiFi equation tests,
9/9 pass; (2) 15/15 compiled-ns-3 versus independent-Python LiFi comparisons;
(3) integrated three-RAT mapping with 9/9 application flows mapped; (4)
byte-identical same-seed repeatability; and (5) a complete W4C sweep with
48/48 configurations and 432/432 mappings passing. The GNPy track is reported
separately: artifact uniqueness and warning audits are complete, but public
GNPy versions cannot load the released equipment file, so independent GNPy
numerical replay is not claimed.

**Exact manuscript change/location.** Synthetic GNPy results;
`sec:ns3_wireless`; Table~\ref{tab:ns3_validation}; W4B/W4C evidence under
`/home/ubuntu/Desktop/LLM Driven wireless environment generation/`.

**Evidence/result.** W4C confirms the final synthetic wireless structural and
equation checks. E4 records the 96-case GNPy compatibility failure under
GNPy 2.14.2 and the matching 2.13.0 check.

**Limitation.** The wireless checks establish implementation consistency and
reproducibility under declared assumptions, not physical-model fidelity. The
GNPy numerical replay gap remains. The local ledger and earlier wireless
response use the R3C4 identifier differently; the original letter must be
used to finalise the numbering.

**Status.** `STILL_PARTIAL` for the combined generated-data concern because
the GNPy numerical replay is unavailable; the wireless component is closed.

### R3C5 — The Abstract must distinguish implemented, evaluated, demonstrated, and proposed elements.

**Response.** The Abstract and framework text now distinguish practical data
organisation, constructed semantic evaluation, demonstrated GNPy/ns-3
workflows, and prospective AI/controller integration points. The GNPy
artifact and W4C wireless dataset are reported with their respective
validation limitations.

**Exact manuscript change/location.** Abstract, framework overview, and LLM
evaluation subsection.

**Evidence/result.** The manuscript labels LLM results as feasibility and
does not present prospective closed-loop blocks as evaluated experiments.

**Limitation.** The original reviewer wording should still be checked against
the local normalized ledger.

**Status.** `CLOSED` for active claim separation.

### R3C6 — Sections III and IV-A overlap.

**Response.** Section III gives the framework scope and boundary; Section IV-A
contains the practical architecture and implementation detail. The current
organisation keeps context separate from implementation.

**Exact manuscript change/location.** Sections III and IV-A, especially the
scope-map and architecture paragraphs.

**Evidence/result.** Current headings and transitions distinguish framework
scope from telemetry/storage implementation.

**Limitation.** No new experiment is needed.

**Status.** `CLOSED`.

### R3C7 — AC/DC power details are unnecessary or unsupported.

**Response.** The AC/DC power discussion was removed from the active
manuscript because it is not needed for the paper's dataset or DT claims.

**Exact manuscript change/location.** Practical dataset/architecture text;
no active AC/DC paragraph remains.

**Evidence/result.** The current manuscript contains no AC/DC experimental
claim.

**Limitation.** None for the present scope.

**Status.** `CLOSED`.

### R3C8 — The -5 dBm setting was presented as optimal.

**Response.** We changed the wording to call -5 dBm the operating point used
for that campaign and explicitly state that no optimality claim is made.

**Exact manuscript change/location.** Optical transmission subsection.

**Evidence/result.** The value is described as a selected campaign operating
point, not an optimisation result.

**Limitation.** No optimality study is claimed.

**Status.** `CLOSED`.

### R3C9 — British and American spelling are mixed.

**Response.** Active manuscript prose uses the selected British spelling
convention, including ``organised'', ``generalisation'', ``optimisation'', and
``fibre''. Obsolete commented text is not part of the compiled manuscript.

**Exact manuscript change/location.** Active manuscript text throughout.

**Evidence/result.** The current active text was checked for the reported
spelling variants.

**Limitation.** Bibliography titles are preserved as source metadata.

**Status.** `CLOSED`.

### R3C10 — Use ns-3 terminology and consistent title capitalisation.

**Response.** The final synthetic wireless backend is described as ns-3.44
with CTTC 5G-LENA 5G NR, native Wi-Fi 802.11ax, and an equation-driven LOS
LiFi/OWC model. The preserved LTE/EPC + 802.11n + CSMA-surrogate code is
labelled legacy/development only and is not used as the final synthetic
claim path.

**Exact manuscript change/location.** `sec:ns3_wireless`, Table~\ref{tab:ns3_validation},
wireless figures/captions, and Conclusions.

**Evidence/result.** W4C final evidence reports 48 configurations, 432
application records, and 144 records per branch.

**Limitation.** The LiFi branch is not a complete standardized PHY/MAC and is
not calibrated to the practical testbed.

**Status.** `CLOSED`.

### R3C11 — A placeholder DOI appears on the first page.

**Response.** The DOI template remains commented and therefore does not
appear in the compiled manuscript.

**Exact manuscript change/location.** `JOCN_Telemetry.tex:64-65`.

**Evidence/result.** The current PDF contains no placeholder DOI field.

**Limitation.** The final publisher-assigned DOI will be inserted by the
editorial process.

**Status.** `CLOSED`.

### R3C12 — Three spelling/grammar errors remain.

**Response.** The reported ``includign BER'', ``based over'', and
``formats,i.e.'' issues were corrected or their surrounding sentences were
rewritten in the active manuscript.

**Exact manuscript change/location.** The affected active prose in the
optical/data-generation sections.

**Evidence/result.** No active occurrence of the reported malformed phrases
remains in the current source.

**Limitation.** The original letter should be checked once more because its
full text is not present locally.

**Status.** `CLOSED` subject to final author proofreading.

## Response-level closure statement

For the current bounded manuscript claims, W5C-A does not require a new
experiment. The remaining author actions concern factual source lineage,
external release metadata, unavailable LLM provenance, the original reviewer
identifier set, and the decision whether the paper should retain any claim
requiring independent GNPy numerical replay. The final response must preserve
the distinction between measured practical data, constructed optical--wireless
interoperability, and synthetic DT outputs.
