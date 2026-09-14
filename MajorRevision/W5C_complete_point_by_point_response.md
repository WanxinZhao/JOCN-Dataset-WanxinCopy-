# Complete point-by-point reviewer response

## Source note

The original reviewer text was checked against
`C:/Users/admin/.codex/attachments/87037826-6321-4f1f-8d5b-da6ac392b380/pasted-text.txt`.
Reviewer 3 Comment 4 requests independent correctness validation of generated
data; the response therefore reports the GNPy and wireless evidence tracks
together under that identifier.

<!-- Superseded W5C-A source note:

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
-->

## Reviewer 1

### R1C1 — The cross-domain meaning is unclear because the three datasets came from independent campaigns.

**Response.** We agree that the practical datasets must not be presented as a
single contemporaneous optical--wireless measurement. We now define
``cross-domain'' in two bounded senses: common repository/metadata and a
constructed sequence-aligned interoperability benchmark. The optical and
wireless files are read separately and their ordered records are mapped by
relative sequence position; no timestamp equality, optical-to-wireless signal
conversion, physical causal relation, or simultaneous campaign is claimed.
The public release and manuscript now distinguish two campaigns on the same
339-km NDFF loop: the earlier 1,373-record, four-channel, 15-minute product
from 2023--2024, and the separate Christmas 2025 eight-channel source used by
E1/E2. The latter contains 20,960 valid records, retains real timestamps from
2025-12-22 to 2026-01-24, and was not resampled to 15-minute intervals.

**Exact manuscript change/location.** Abstract; Introduction; `sec:SemanticModules`
benchmark paragraph; `tab:dataset_summary`; practical-data subsection. The
implementation is `MajorRevision/run_e1_e2.py:180-210`.

**Evidence/result.** The Christmas 2025 source is published byte-identically
under `OTN Monitoring Data_one_month/NDFF_Voyager_Christmas_2025/`, with
SHA-256 `879d7b6143b04b995165360d1600b81b8134312fed08b2bdeb577b5cb8b6e209`.
W1A found zero timestamp intersection with the wireless file and verified that
mapping uses `round(linspace(...))`; the benchmark has 2,848 one-step samples.

**Limitation.** The benchmark remains a positional interoperability test, not
a contemporaneous or causal optical--wireless measurement.

**Status.** `CLOSED`; the source lineage and constructed-benchmark boundary
are both explicit.

### R1C2 ? Report the LLM model, calls, failures, cost, latency, human intervention, and a script baseline.

**Response.** We limit the LLM contribution to a feasibility demonstration and retain the demonstrated Agent architecture. We added a separately identified new OpenAI reproduction using `gpt-4o-mini-2024-07-18`, temperature 0.2, timeout 90 s, maximum three attempts and strict mode. Six complete request/response pairs record six successful first attempts, 108,308 tokens, 26.22 s summed API latency and estimated text-token cost USD 0.01726635. These are observations from one invocation, not an estimate of general reliability. An earlier interrupted two-call invocation is reported separately (4,057 tokens; USD 0.0009339); the known API subtotal is USD 0.01820025, excluding computation, labour and unrecorded activity.

We disclose the environment, spectrum, extraction and single-channel repairs, manual interruption/resume, recovery diagnostics and replay of nine failed simulator cases. The resumed invocation's 2 h 1 min 25.3 s interval includes troubleshooting. Correcting a deterministic sweep override subsequently required an 85 min 9.0 s second-round replay with no new LLM calls. The original last Reflection was not recomputed on corrected data; convergence and unattended operation are not claimed.

The corrected set at -6.5/-6.0/-5.5 dBm exactly matches an independently specified 6,144-key Cartesian product. The combined 8,192 records contain 2,048 repeated keys (25%). Deterministic configuration enumeration takes a median 0.00145 s over 31 local timing repeats; this excludes intent parsing and GNPy, is not an end-to-end comparison, and does not constitute independent LLM trials.

**Exact manuscript change/location.** Evaluation Protocol and Reproducibility Scope; `tab:llm_trace`; `tab:llm_baseline`; corrected GNPy results and `fig:usecase1`; Conclusions. Supporting material: `MajorRevision/13_E6_demonstration_revision.md` and `MajorRevision/E6_llm_trace_reproduction/corrected_analysis/`.

**Evidence/result.** The source archives are released at `WanxinZhao/JOCN-DATASET-Code@82914127b70acf3b220bc09a56a179cb7abd1252`; archive hashes, repaired source hashes, exact-set coverage and scenario/request/CLI/metric power consistency were checked. Both precision and recall are 1.0.

**Limitation.** OpenAI is author-reported for the historical run; the new API evidence does not verify its missing dated snapshot, usage or operator history. API success and final zero residual simulator errors after repair do not imply an error-free development history, physical calibration or an advantage over scripting.

**Status.** Addressed within the adopted feasibility-demonstration scope; historical missing metadata and the absence of convergence/repeated-trial evidence remain explicitly disclosed.

### R1C3 — Add a dataset summary table and machine-readable metadata such as Croissant.

**Response.** We added the dataset summary table and retained
`MajorRevision/croissant_metadata.json`. The public dataset repository now
contains the final W4C release at `W4C_THREE_RAT_SWEEP/`. The
Croissant record identifies the two distinct 339-km Voyager products, the
materialised constructed-fusion table, final application-flow table, run-level
and LiFi summaries, structural validation, source documentation, and the
complete application/optical-state field dictionary with units. Unknown raw
practical-telemetry units and formal licence terms remain explicitly marked
rather than fabricated.

**Exact manuscript change/location.** `tab:dataset_summary` and the practical
dataset subsection. The complete machine-readable audit is
`W5C_dataset_metadata_matrix.md`.

**Evidence/result.** The current Croissant file documents the processed
wireless table, both Voyager campaigns, the 2,848-row/52-field materialised benchmark,
E1/E2 result tables, deduplicated GNPy audit CSV, recovered GNPy replay, and
the public W4C release with recorded paths, sizes, hashes, and field units.
The final W4C row reports 48 configurations, 432 application-flow records,
and 624 raw FlowMonitor rows.

**Limitation.** Exact aggregate counts and sizes for the externally referenced
986-km and urban-sensing collections are not consolidated in the manuscript.
The practical wireless source does not preserve formal units for every raw
field, and no standard LICENSE/SPDX file is present; these facts are stated as
release limitations rather than inferred.

**Status.** `PARTIALLY_CLOSED`; the Voyager, constructed-fusion, and W4C
release metadata are closed, while externally referenced collection totals,
undocumented practical-field units, and formal licence terms remain author
confirmation items.

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

**Evidence/result.** E1 records 1,698/560/570 evaluated samples, 20 purged
boundary records, ten seeds, and train-only preprocessing. The byte-identical
20,960-record Voyager source and the 2,848-row/52-field materialised benchmark
are now public. The table records both source-row indices, split membership,
and the training-only Q/BER thresholds. The optical and wireless campaigns
remain separate and the benchmark uses positional sequence mapping.

**Limitation.** No matched raw-wireless-only ablation exists, so no incremental
fusion gain is claimed; the labels remain rule-derived rather than field fault
annotations.

**Status.** `CLOSED`; the source snapshot, construction, labels, settings, and
leakage-free temporal protocol are reproducible within the stated boundary.

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

### R3C3 ? The LLM framework is insufficiently evaluated.

**Response.** We adopt the reviewer's suggested feasibility-demonstration scope. The retained Agent architecture demonstrates natural-language-to-simulator workflow execution; we do not claim superiority over scripts, autonomous repair, convergence or general reliability. As detailed under R1C2, the new six-call trace reports exact prompts/responses, dated model, settings, actual attempts, tokens, latency and estimated cost, while manual repair/resume and a later zero-new-call corrected replay are separately accounted for.

**Exact manuscript change/location.** Abstract; Evaluation Protocol and Reproducibility Scope; `tab:llm_trace`; `tab:llm_baseline`; GNPy results; Conclusions. Existing wireless results remain in `sec:ns3_wireless` and `tab:ns3_validation`.

**Evidence/result.** The corrected optical demonstration covers exactly 6,144 expected unique configurations in 8,192 execution records (25% repeated). It contains 6,120 unique `ok` and 24 expected all-off `no_signal` configurations. No configuration keys are missing or extra. W4C retains its independent wireless evidence: 48 configurations and 432 application-flow records with 432/432 mapping passes. Those simulator checks do not establish LLM efficacy.

**Limitation.** The original final Reflection used pre-correction results and requested another refinement at the configured two-iteration cap. It was not rerun on corrected results. The experiment does not supply independent LLM repetitions or single-LLM/no-Reflection ablations, and the historical API trace remains unavailable. The deterministic timing is enumeration only.

**Status.** Addressed through the explicitly bounded feasibility demonstration, additional trace disclosure and corrected configuration-set comparison.

### R3C4 — The generated data lack independent correctness validation.

**Response.** We agree that successful execution alone cannot detect a
plausible but incorrectly configured simulator, KPI extractor, or flow
mapping. The final wireless track adds: (1) independent LiFi equation tests,
9/9 pass; (2) 15/15 compiled-ns-3 versus independent-Python LiFi comparisons;
(3) integrated three-RAT mapping with 9/9 application flows mapped; (4)
byte-identical same-seed repeatability; and (5) a complete W4C sweep with
48/48 configurations and 432/432 mappings passing. For GNPy, we recovered the
legacy equipment and scenario artifacts and replayed 96 cases stratified by
path, modulation/spectrum configuration, launch power, and active-channel
load. Official GNPy v2.12 at commit
`7ce665010970f57e46672db1ec0864ae448077e6` completed 96/96 and reproduced the
archived GSNR values with mean/max absolute errors of 0.00015/0.00050 dB. A
schema-corrected GNPy 2.14.2 run also completed 96/96, with mean/max GSNR
differences of 0.628/1.435 dB.

**Exact manuscript change/location.** Synthetic GNPy results;
Table~\ref{tab:gnpy_replay}; `sec:ns3_wireless`;
Table~\ref{tab:ns3_validation}; `MajorRevision/E5_recovered_gnpy_replay/`;
and public W4C evidence under `W4C_THREE_RAT_SWEEP/`.

**Evidence/result.** W4C confirms the final synthetic wireless structural and
equation checks. E5 records 96/96 successful CLI runs in both GNPy replay arms,
case-level comparisons, frozen dependencies, source manifests, input files,
and logs.

**Limitation.** The wireless checks establish implementation consistency and
reproducibility under declared assumptions, not physical-model fidelity. The
GNPy v2.12 arm is an exact-output compatibility reconstruction rather than
proof of the unavailable original run commit, while the v2.14.2 differences
and persistent EDFA/ROADM warnings prevent a warning-free physical-calibration
claim.

**Corrected E6 scope.** The new corrected second-round set is audited separately: 6,144 unique configurations, 6,120 active scenarios with matching power across scenario/request/CLI/returned metric metadata, and 24 expected all-off cases. All 6,120 corrected result files retain EDFA and ROADM warnings. The historical 96-case comparison does not independently validate the changed E6 power sweep or its local single-channel patch. Corrected figures use signal-bandwidth metrics and second-round unique records only.

**Status.** `CLOSED_WITH_DECLARED_MODEL_LIMITATIONS`; independent numerical,
equation, mapping, repeatability, and version-sensitivity evidence is now
reported for both generated-data tracks.

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

**Limitation.** The distinction is terminological and evidential; it does not
add scalability or field-validation results that were not actually measured.

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

For the current bounded manuscript claims, no new experiment is required. The
Voyager lineage, constructed-benchmark release, reviewer identifier set, GNPy
numerical replay, and final W4C release are closed. Remaining author actions
are limited to exact metadata for externally referenced collections,
undocumented practical-wireless units, formal licence terms, and any historical
LLM run traces that may still exist. The final response preserves the
distinction between measured practical data, constructed optical--wireless
interoperability, and synthetic DT outputs.
