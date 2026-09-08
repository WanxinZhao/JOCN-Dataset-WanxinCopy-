# W2 wireless ns-3 manuscript revision

## Outcome and scope

W1 scientific verdict retained: **PASS_WITH_LIMITATIONS**. W2 integrates existing validation into the manuscript; no simulations, optical experiments, semantic-fusion experiments, source-data changes, commits, or pushes are performed.

Edited manuscript: `/tmp/jocn-w0-github/JOCN_Telemetry.tex`.
Repository: `https://github.com/WanxinZhao/JOCN-Dataset-WanxinCopy-.git`.
Base HEAD: `7b2787ee93ac9b40711170ca545cab9df4f795c4`; branch `main`; worktree clean before W2.

The research-evidence-loop skill guided claim-to-artifact mapping and retention of negative findings. The PDF skill is used for build/layout verification. The W1 report was read in full before editing.

## Manuscript changes

| Location | Scientific addition/change | Reviewer |
|---|---|---|
| Existing dataset table, `tab:dataset_summary` | One synthetic-only entry: ns-3.44, three named branches, 48 configurations, 432 application versus 624 raw flow records, seeds, output types, methodology cross-reference; no invented size/licence | R1 dataset summary |
| Wireless use case, `sec:ns3_wireless` | Full parameter sweep, RandomWalk2d bounds/speeds, three CPEs, three branches, per-flow UDP load/packet size, application/simulation times, link rates/delays, seed/default-run handling | R3C3, R3C4 |
| Same subsection | Effective command-line overrides are essential; stale base metadata disclosed, not described as uniformly consistent | R3C4 reproducibility |
| KPI paragraph | Exact throughput/delay/jitter definitions, IP-byte rather than payload throughput, qualified FlowMonitor-reported packet-loss ratio, explicit cutoff/loss-detection limitation | R3C4 |
| Validation paragraph and `tab:ns3_validation` | Independent reconstruction, mapping check, representative replay, repeatability, separately written ns-3 reference, exact W1 coverage/errors and limitations | R3C4; simulation side of R3C3 |
| Wireless results/limitations | Configuration-specific trends and a three-seed mean/SD; no universal ranking, calibrated testbed emulation, or physical LiFi validation | R3C3, R3C10 |
| Conclusions | Replaced only the ns-3 sentence with the bounded correctness/reproducibility conclusion | R3C4 |

The optical use case, practical/semantic sections, original dataset-table rows, and other conclusion sentences remain unchanged. No abstract or optical evaluation edits were needed.

## Table/figure decision

One new compact table, “Validation of the ns-3 synthetic wireless dataset,” replaces reliance on the old single-run performance illustration. The old `fig:ns3_results` figure inclusion/caption and its single-run ranking narrative were removed from the manuscript; `Figures/fig_ns3_results.png` is preserved unchanged. No new or replacement performance figure is added. W1-traceable sweep trends and seed sensitivity are reported in prose. This avoids retaining unsupported “idealised upper-bound” language and an unspecified single-run interpretation. A synthetic entry is also added to the existing summary table, not a second new table.

## Exact evidence map

Manuscript-ready synthetic dataset metadata (the manuscript distributes these fields between the existing summary-table entry and the wireless methodology):

| Field | Entry |
|---|---|
| Dataset | Synthetic wireless DT parameter sweep |
| Generator | ns-3.44 |
| Access branches | LTE/EPC; Wi-Fi 802.11n; CSMA-based LiFi surrogate |
| Run configurations | 48 |
| Application-flow records | 432 |
| Raw FlowMonitor records | 624, including 192 infrastructure/control flows |
| Seeds | 3: 1, 2, 3 |
| Offered load | 2/5/10/20 Mbps per application flow |
| Mobility | RandomWalk2d; 50 m × 50 m; 0.5/3 m/s |
| Surrogate rate | 50/100 Mbps |
| Packet size | 1024 bytes |
| Simulation duration | 10 s; applications approximately 1–10 s |
| Outputs | FlowMonitor XML; per-flow KPI CSV; scenario/config metadata; aggregated CSV |
| Validation | Full independent FlowMonitor reconstruction; three representative replays; same-seed repeatability; independent hand-written ns-3 reference |

Evidence root: `/home/ubuntu/Desktop/LLM Driven wireless environment generation/W1_NS3_VALIDATION/`.

| Claim | Artifact/field | Boundary |
|---|---|---|
| 48 runs, 624 raw and 432 application flows | `kpi_recomputation_summary.json`: `run_count`, `raw_flow_rows`, `application_flow_rows` | 192 infrastructure/control flows excluded from application statistics |
| All packet counters exact | Same JSON: `metrics.{tx_packets,rx_packets,lost_packets}.{all_flow_rows,application_flow_rows}` | rxBytes reconstructed from XML, not compared to nonexistent KPI CSV column |
| App max absolute errors: 5.5697687857403366e-5 Mbps, 0.00316444701797991 ms, 1.100128369690978e-5 ms | Same JSON: throughput/delay/jitter `application_flow_rows.maximum_absolute_error`; full details `kpi_recomputation_comparison.csv` | Maximum relative error 6.317747754250935e-6; 50 delay rows exceed initial 1e-4-ms screen; control-flow throughput max relative error 0.28 |
| All 432 terminal accounting differences nonzero | Same JSON: `packet_accounting`; `flowmonitor_recomputed.csv` | lostPackets is not terminal tx-rx; do not claim zero terminal loss |
| No missing/extra/duplicate effective keys or mapping issues | `sweep_consistency_summary.json`, `sweep_consistency.csv` | Base load/mobility/rate stale in 36/48/24 runs; preserve effective overrides |
| 3/3 representative replays, 27 flows, zero XML-derived KPI deltas | `replay_report.md`, `replay_results.csv` | Tested ns-3.44/GCC 15.2.0/default build, not all-platform determinism |
| Two fixed-config executions identical | `repeatability.csv` | Nine flows, seed 2, load 10 Mbps, speed 3 m/s, surrogate rate 100 Mbps |
| 5 configuration + 63 KPI checks consistent | `independent_reference/report.md`, `comparison.csv`, `reference.cc` | Same stock simulator and modelling assumptions; not independent physical validation; five checks do not exhaustively test every PHY setting |
| Wi-Fi throughput 10.140 ± 0.218 Mbps | `seed_sensitivity.csv`: Wi-Fi/throughput row `seed_mean_mean`, `seed_mean_std` | Three seed means, not nine independent seeds |
| Configuration-specific saturation, jitter and modelling boundary | `grouped_kpi_summary.csv`, `sweep_sanity_report.md`, `ns3_claim_boundary.md` | No universal branch ranking or physical upper bound |

## Claims removed or narrowed

- “LiFi-like”/unqualified surrogate descriptions replaced by CSMA-based LiFi surrogate.
- Unsupported physical upper-bound interpretation removed.
- Unqualified highest/lowest delay/jitter ordering replaced by configuration-specific observations; surrogate jitter is not uniformly near zero.
- Successful execution is no longer the only correctness evidence.
- No equality of FlowMonitor lostPackets and terminal tx-rx; no zero terminal-loss claim.
- No claim that all continuous metrics are exactly equal across independent XML/CSV reconstruction.
- No claim that every base JSON field matches executed values.
- No assertion of historical reflection/retry success based only on retained successful runs.
- No assertion of physical testbed validation or LLM superiority from simulator reproducibility.

## Remaining limitations and submission handoff

The 10-s cutoff does not evaluate terminal packet loss. The surrogate lacks optical LOS/FOV geometry, photodiode response, optical modulation, shot noise, blockage, and calibrated optical channel/errors. LTE/EPC is not 5G NR, and Wi-Fi 802.11n is not the practical Wi-Fi 6 system. Three seeds and three replayed configurations bound the reproducibility evidence. The independent reference shares simulator libraries/assumptions. The archive retains stale base JSON/default values; the effective-parameter recipe must accompany the release. No terminal-loss rerun or sweep expansion is needed for the narrowed manuscript claim.

Before submission, release/package the W1 parser, replay harness, reference source and comparison artifacts alongside the dataset; this W2 task does not publish or push them. Historical LLM cost/tokens/latency remain unmeasured here. Synthetic postprocessing scores are not independent ground truth; no new score/semantic claims are introduced.

## Verification

- `git diff --check`: PASS.
- Scope comparison against HEAD: only the new synthetic summary row, wireless subsection, and ns-3 conclusion sentence differ, apart from a trailing blank line. Optical/semantic text and all experiment/data files remain unchanged.
- Standard build command: `latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=output/pdf JOCN_Telemetry.tex`, working directory `/tmp/jocn-w0-github`.
- Clean standard build: **BLOCKED_BY_PREEXISTING_BIBLIOGRAPHY_ERRORS**. BibTeX reports 26 repeated-entry errors in unchanged `sample.bib` (starting line 539). Subsequent pdfLaTeX encounters unescaped `&` from journal names in that same file (e.g. lines 168/421), emitted at generated `.bbl` lines 13/146. The `.bib`, bibliography style and class are unmodified.
- Layout-only workaround: escaped the two bare ampersands in the generated, ignored `output/pdf/JOCN_Telemetry.bbl`, then ran `pdflatex -interaction=nonstopmode -halt-on-error -output-directory=output/pdf JOCN_Telemetry.tex` to stabilize cross-references. This is a preview workaround, not a clean-build fix; rerunning BibTeX can recreate the error.
- Preview: `output/pdf/JOCN_Telemetry.pdf`, 13 pages. Rendered and visually checked pages 8 (dataset table), 11 (wireless methodology/validation table), and 12 (wireless limitations/conclusion); no clipping or table overlap. The final preview log has no undefined references/citations or overfull boxes; font-substitution/underfull-box warnings remain. Preview images are in untracked `output/w2_preview/`.
- No simulations were executed in W2. No commit or push was made. The old figure asset remains untouched. The two requested Markdown documents and preview PNGs are new untracked files; the PDF and usual LaTeX build products are ignored by the repository.

## Final status

```text
W2_WIRELESS_VERDICT=COMPLETE_WITH_BUILD_LIMITATION; SCIENTIFIC_VERDICT_PASS_WITH_LIMITATIONS
R3C4_CORRECTNESS_RESPONSE=ADDED_WITH_EXACT_W1_EVIDENCE_AND_LIMITATIONS
R3C3_SIMULATION_EVIDENCE=ADDED; NO_LLM_COST_OR_SUPERIORITY_CLAIM
R3C10_TERMINOLOGY=LOCKED_IN_ACTIVE_WIRELESS_TEXT
FLOWMONITOR_LOSS_WORDING=REPORTED_RATIO_NOT_TERMINAL_LOSS
PRACTICAL_VS_SYNTHETIC_BOUNDARY=EXPLICIT
NEW_VALIDATION_TABLE=ADDED_TABLE_4
UNSUPPORTED_CLAIMS_REMOVED=YES; UPPER_BOUND_AND_UNQUALIFIED_BRANCH_RANKING
MANUSCRIPT_BUILD_STATUS=STANDARD_BUILD_BLOCKED_BY_EXISTING_BIBLIOGRAPHY; PREVIEW_PDF_VERIFIED
```
