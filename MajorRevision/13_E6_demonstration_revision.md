# E6 demonstration: corrected data, accounting and manuscript integration

## Adopted scope

The LLM workflow is a feasibility demonstration. The existing Agent architecture,
role names and architecture figure are retained. The demonstration does not
establish an advantage over deterministic scripting, unattended operation,
independent repeated-trial reliability, or Reflection convergence. This revision
updates the configuration baseline, execution accounting and numerical results.

## Evidence and reproduction

The input evidence is repository commit
`82914127b70acf3b220bc09a56a179cb7abd1252`. Original archives and earlier reports
remain historical records. For the corrected numerical results use report 12
and `E6_corrected_second_round_20260914.tar.gz`; for the six API calls and
recovery history use report 11 and the completed-reproduction archive. Report 11's
description of a Planner/Expander discrepancy is superseded by report 12: the
saved model responses agreed; deterministic post-processing overrode their sweep.

The manuscript release includes the exact script in
`MajorRevision/E6_llm_trace_reproduction/corrected_analysis/audit_e6_corrected.py`.
Copy it to `revision_experiments/audit_e6_corrected.py` in a checkout of the cited
code repository at the evidence commit above. Run from that code repository
root, using Python 3.12 with matplotlib installed:

```text
python revision_experiments/audit_e6_corrected.py
```

Outputs are in `revision_experiments/E6_llm_trace_reproduction/corrected_analysis/`.
The audit verifies both archive hashes and the two repaired source-file hashes,
then reads the archives without extracting executable contents. It makes no API
calls and runs no simulations. `analysis_requirements.txt` records the analysis
environment, which is distinct from the Linux GNPy execution environment.

## 1. Corrected configuration baseline

The independently specified expected set is Bristol-origin paths to Bradley
Stoke, Froxfield, Reading and Powergate, Voyager transmitters, QPSK/37.5-GHz and
16QAM/50-GHz configurations, all 256 eight-slot binary patterns, and powers
`[-6.5, -6.0, -5.5] dBm`. Expectations are not inferred from the observed rows.

| Method/data | Simulation execution records | Unique configurations | Repeated records beyond first | Set precision/recall |
|---|---:|---:|---:|---|
| Deterministic enumeration | 0 | 6,144 | 0 | 1.0 / 1.0 |
| Corrected E6 two-round history | 8,192 | 6,144 | 2,048 (25%) | 1.0 / 1.0 |
| Corrected second round used for plots | 6,144 | 6,144 | 0 | 1.0 / 1.0 |

All first-round keys at -5.5 dBm recur in the second round. Unique keys exclude
iteration and scenario ID. The final unique table uses second-round results;
both the figure and summary statistics use this same table. The 24 all-off
configurations remain in the coverage denominator and are excluded from numeric
GSNR/OSNR summaries. Of the 6,144 unique configurations, 6,120 return `ok` and 24
return expected `no_signal`. The combined history has 8,160 `ok` and 32
`no_signal` records. An `ok` status denotes returned metrics, not validated
physical accuracy.

The local enumeration microbenchmark takes a median of approximately 0.00145 s
over 31 repeats (Python 3.12.10, Windows; individual measurements retained in
`enumeration_timings.csv`). It measures configuration-tuple creation only,
excluding archive I/O, set comparison, natural-language interpretation and GNPy.
These 31 repeats are not independent LLM trials. This differs from E3's old
0.0063-s measurement in implementation/environment and must not be interpreted
as a performance improvement or compared with end-to-end simulation time.

## 2. API, timing, failures and human intervention

| Stage | LLM API calls | Tokens | Estimated text-token cost (USD) | Time and outcome |
|---|---:|---:|---:|---|
| Earlier interrupted invocation, report 09 | 2 | 4,057 | 0.00093390 | 10.04 s summed API latency; workflow interrupted after 344 CLI import failures and one all-off result; exact workflow duration unavailable |
| New two-round reproduction with manual recovery, report 11 | 6 | 108,308 | 0.01726635 | 26.22 s summed API latency; 2 h 1 min 25.3 s run interval includes interruption/troubleshooting/resume |
| Corrected second-round replay, report 12 | 0 new calls | 0 new API tokens | 0 additional API token cost | 85 min 9.0 s; saved Reflection 1, Planner 2 and Expander 2 responses reused |
| Known two-invocation API subtotal | 8 | 112,365 | 0.01820025 | Excludes unrecorded activity and non-API compute; not a complete project cost |

Costs are estimates from the pricing snapshot retained with the September 13
run, not invoices or current-price claims. They exclude local computation,
labour and any unrecorded historical/provider activity. The six-call statistics
describe the resumed reproduction, not all development attempts.

The fixed model is `gpt-4o-mini-2024-07-18`, temperature 0.2, timeout 90 seconds,
maximum three attempts per call, strict mode without silent rule fallback.
Planner, Scenario Expander and Reflection each have two recorded calls. All six
API attempts succeeded on their first attempt. This sample observation is not an
estimate of general workflow reliability. The second expansion request contains
96,716 input tokens; there is no measured communication-efficiency advantage.

Human intervention includes environment/package repair; omission of inactive
spectrum slots; the CLI received-power extraction fix; the single-channel GNPy
fix; manual interruption and recovery; switching the resumed data source to
manifest-hashed local files; correcting the recovery log callback; rerunning nine
original simulator failures; and correcting the deterministic sweep override
followed by the second-round replay. Initial and recovery diagnostics remain
auditable. The manifest records one interruption-recovery event, but this is not
a count of all operator actions. Exact human effort and every intervention
timestamp were not measured. Final zero residual execution errors must not be
reported as a zero-error development history or as unattended success.

The original Reflection 2 saw the pre-correction results and requested `refine`;
the configured cap was two iterations. No new Reflection 2 was run on the
corrected data. The evidence establishes a reflection-proposed second-round
sweep and its corrected execution, not convergence or autonomous software repair.

## 4. Corrected numerical results and figures

The audit checks scenario power against request JSON, the CLI `-po` argument and
returned metric metadata for all 6,120 active scenarios: zero mismatches. The
24 all-off configurations do not invoke propagation. This is configuration
consistency validation, not an independent optical propagation implementation.

`usecase1_corrected.pdf` and its 400-dpi PNG provide the replacement result
figure; the separate Agent architecture figure is unchanged. Panel (a) retains
the request--scenario-expansion--DT-execution--dataset-output workflow, and
panels (b)--(d) show joint-format GSNR distributions, the corrected power sweep,
and QPSK channel-loading means. `corrected_power_metrics.pdf` and PNG
add route-level GSNR and OSNR sweeps. Metrics use signal bandwidth throughout.
Each configuration first averages its active-channel metrics; plotted means then
weight configurations equally. Boxplots show medians, quartiles and 1.5-IQR
whiskers, with outlier markers omitted. They are descriptive distributions, not
confidence intervals over independent LLM runs.

| Destination | Mean GSNR at -6.5 dBm | At -6.0 dBm | At -5.5 dBm | QPSK GSNR at -5.5 dBm: 1 → 8 active channels |
|---|---:|---:|---:|---|
| Bradley Stoke | 25.9532 | 25.3140 | 24.6027 | 26.3425 → 22.5690 dB |
| Froxfield | 7.1633 | 7.1530 | 7.1393 | 9.7788 → 4.0490 dB |
| Reading | 7.0279 | 7.0424 | 7.0481 | 9.6800 → 3.9620 dB |
| Powergate | 6.6511 | 6.7980 | 6.8888 | 9.5175 → 3.8030 dB |

Power-column means average both joint format/slot configurations and all 255
active patterns per format. Effects are route dependent: lower tested power
increases mean GSNR on Bradley Stoke, while Powergate shows the opposite trend.
Three tested points do not establish a globally optimal launch power. The 3,060
paired joint-format comparisons have mean/max absolute GSNR differences of
0.54958/1.088 dB; these replace the historical 0.4779/0.8080 dB values only when
describing the corrected E6 set. The comparison changes both modulation and
slot width, so it is not a modulation-only effect.

The corrected archive has 6,120 CLI result files. All contain EDFA minimum-gain
warnings (48,960 occurrences) and unmet ROADM target-power warnings (12,240
occurrences). These new counts must not be confused with E4's historical audit.
The E5 96-case v2.12/v2.14.2 comparisons retain their original meaning and
results, but are explicitly historical-archive numerical audits. They do not
independently validate the changed E6 sweep or the local single-channel patch.

## Suggested reviewer response

### R1: LLM details and conventional scripting baseline; R3 comment 3

We have explicitly limited the LLM contribution to a feasibility demonstration
and retained the demonstrated Agent architecture. We now report the dated model
snapshot, settings, complete rendered prompts and responses, actual attempts,
token usage, per-call latency, estimated cost, manual interventions and failed
execution/recovery history for a separately identified new reproduction. The
corrected 6,144-configuration set exactly matches an independently specified
deterministic enumerator. We distinguish the 8,192 execution records from the
6,144 unique configurations and report the 25% repetition rate. The scripting
baseline performs configuration enumeration only; no end-to-end speed advantage
is asserted. Six successful API calls and zero residual simulator errors after
repair are reported as observations, not as repeated-trial or unattended success
rates. The corrected replay makes no new API calls and does not establish
Reflection convergence. Historical API evidence remains separately labelled.

### R3 comment 4: independent correctness and provenance

We retain the 96-case independently generated numerical replay with pinned
GNPy versions and disclose its equipment changes and residual warnings. We
separately report the corrected E6 set, its input/source/archive hashes, and
configuration consistency checks over all active scenarios. We do not extend
the historical 96-case findings into a claim that every corrected E6 sample has
independent physical validation. Updated figures and tables use the corrected
unique configurations and state the signal-bandwidth metric definition.

### R3 comments 5 and 8: scope and optimality

The abstract and conclusions identify the LLM contribution as a feasibility
demonstration with manual recovery and corrected deterministic replay. We report
route-dependent sensitivity over three tested power values and make no global
optimal-power, calibrated-physical-accuracy or scalability claim.

## 中文执行说明

本轮落实第 1、2、4 点：修正版基线与去重、分阶段调用/耗时/人工干预披露、
结果图和正文数值更新。保留既有 Agent 架构、命名及架构图，不新增架构消融、
LLM 调用或光层仿真。报告 09–12 与原始归档保留作为历史证据；本报告和新分析
目录作为当前修正版解释入口。论文中独立的无线及语义实验不在本次修改范围内。
