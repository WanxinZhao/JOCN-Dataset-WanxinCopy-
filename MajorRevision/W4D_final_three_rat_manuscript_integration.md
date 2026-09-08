# W4D final three-RAT wireless manuscript integration

## 1. Final scientific verdict

**Verdict: `PASS_W4D_WIRELESS_INTEGRATION_WITH_KNOWN_PREEXISTING_BIBLIOGRAPHY_BLOCKER`.**

The active manuscript and wireless reviewer response now use the W4C
three-RAT synthetic experiment as the final wireless simulation result. The
old LTE/EPC + 802.11n + CSMA-based LiFi-surrogate experiment is no longer on
the active final-claim path and is explicitly scoped as a preserved
legacy/development baseline in the archival commented conclusion and the
reviewer response.

The integrated claims are supported by the authoritative W4C report and
artifacts: ns-3.44 with CTTC 5G-LENA `5g-lena-v4.0.y`, native
`WIFI_STANDARD_80211ax`, and an uncalibrated equation-driven LOS LiFi/OWC
model; 48 configurations; 432 application-flow records; 624 raw
FlowMonitor rows; 144 rows per branch; 9/9 application-flow mappings per
run; 9/9 independent LiFi equation tests; 15/15 compiled-probe/reference
comparisons; and byte-identical fixed-seed repeat outputs.

The wireless scientific revision is complete. The only build limitation is
pre-existing, non-wireless bibliography damage in `sample.bib`: duplicate
BibTeX keys and unescaped ampersands in existing entries. A PDF was still
generated and visually inspected, but `latexmk` returns nonzero until that
unrelated bibliography issue is repaired.

## 2. Manuscript consistency audit

The active manuscript was checked against:

- `/home/ubuntu/Desktop/LLM Driven wireless environment generation/WIRELESS_REVISION_W4A_NR_WIFI_LIFI_BACKEND_QUALIFICATION.md`;
- `/home/ubuntu/Desktop/LLM Driven wireless environment generation/WIRELESS_REVISION_W4B_THREE_RAT_IMPLEMENTATION.md`;
- `/home/ubuntu/Desktop/LLM Driven wireless environment generation/WIRELESS_REVISION_W4C_FINAL_SWEEP.md`;
- `/home/ubuntu/Desktop/LLM Driven wireless environment generation/W4C_THREE_RAT_SWEEP/`.

Evidence-to-text anchors in the final source are:

| Manuscript location | Integrated content |
|---|---|
| `JOCN_Telemetry.tex:97` | Contribution now identifies the 5G NR, Wi-Fi 6/802.11ax, and equation-driven LOS LiFi/OWC synthetic scenario. |
| `JOCN_Telemetry.tex:339-344` | Dataset table separates measured wireless data from the synthetic three-RAT DT row and reports 48/432/624. |
| `JOCN_Telemetry.tex:497-512` | W4C backend, topology, parameters, workload, LiFi equations, and uncalibrated-model boundary. |
| `JOCN_Telemetry.tex:514-515` | Throughput, delay, jitter, and FlowMonitor-reported loss definitions; no terminal-loss relabelling. |
| `JOCN_Telemetry.tex:517-520` | W4C validation evidence and bounded interpretation. |
| `JOCN_Telemetry.tex:522-542` | Table 4 with backend, equation, reference, mapping, repeatability, and full-sweep evidence. |
| `JOCN_Telemetry.tex:544-560` | W4C factor results, Figures 8–9, and one consolidated wireless limitation paragraph. |
| `JOCN_Telemetry.tex:574` | Active conclusion uses the W4C final stack and bounded correctness/reproducibility claim. |

Required factual anchors are consistent: ns-3.44; four offered loads
(2/5/10/20 Mbps); mobility 0.5/3 m/s; LiFi FOV 40/70 degrees; seeds 1/2/3;
1024-byte packets; 10-s simulations; 48 configurations; 432 application
flows; 624 raw FlowMonitor rows; 3/3 representative W4B qualification
coverage where cited; and final W4C 9/9, 15/15, 48/48, and 432/432 checks.

## 3. Final synthetic backend and claim boundary

The final active method is:

- **5G NR:** CTTC 5G-LENA `5g-lena-v4.0.y` on ns-3.44, one gNB and three
  UEs, 3.5 GHz, 40 MHz, numerology 1, InH-OfficeOpen, 30 dBm gNB power.
- **Wi-Fi:** native Wi-Fi 802.11ax / Wi-Fi 6 APIs, one AP and three stations,
  5 GHz, 20 MHz, 16 dBm, explicit constant-rate HeMcs0.
- **LiFi/OWC:** equation-driven LOS model with Lambertian emission,
  geometry/FOV, received optical power, detector responsivity, shot and
  thermal noise, SNR, OOK BER, and packet-error probability. The IP/UDP path
  uses a stock point-to-point packet-access abstraction. It is not a
  complete standardized LiFi PHY/MAC and is not calibrated to the practical
  testbed.

The manuscript includes the implemented Lambertian order, LOS gain,
concentrator, received-power, BER, and PER equations at
`JOCN_Telemetry.tex:506-510`, with the related Kahn/Barry and Komine/Nakagawa
references added to `sample.bib`. The model is explicitly described as
uncalibrated.

The practical wireless campaign and generated wireless DT data remain
separate. The synthetic data share the three access technology classes with
the measured testbed, but do not reproduce its measured values or establish
physical-testbed calibration.

## 4. Table 4 status

Table 4 at `JOCN_Telemetry.tex:522-542` is updated from the legacy W1
validation table. It now distinguishes:

1. backend qualification;
2. independent LiFi equation tests;
3. compiled LiFi probe versus independent Python reference;
4. integrated three-RAT flow mapping;
5. same-seed repeatability;
6. complete W4C sweep completion.

It reports 9/9 LiFi unit tests, 15/15 compiled/reference comparisons, 9/9
integrated application-flow mappings, byte-identical fixed-seed outputs, and
48/48 completed configurations with 432/432 mappings passing. The footnote
states that these are implementation, equation, mapping, repeatability, and
coverage checks—not physical-model validation.

The rendered PDF shows Table 4 completely and legibly on page 11. No
material table clipping or overlap was observed.

## 5. Final W4C result integration

Only W4C results are used in the active synthetic wireless result path.
`JOCN_Telemetry.tex:544` reports the observed run-level contrasts from the
W4C analysis, with the run—not individual CPE rows—as the experimental unit:

- from 2 to 20 Mbps, throughput increased by 18.486 Mbps for NR, 0.151 Mbps
  for Wi-Fi 802.11ax, and 15.726 Mbps for LiFi; the Wi-Fi delay and
  FlowMonitor-reported loss ratio increased by 1,653.88 ms and 0.701,
  respectively;
- increasing mobility from 0.5 to 3 m/s changed throughput by 0 Mbps for NR,
  0.00018 Mbps for Wi-Fi, and -2.572 Mbps for LiFi under the selected model;
- narrowing LiFi FOV from 70 to 40 degrees reduced in-FOV and received-packet
  fractions by 0.299 in matched run-level comparisons.

The text correctly explains that these are configuration-specific responses.
It does not assert a universal RAT ranking. It also does not assert that
aggregate LiFi received power or SNR must decrease monotonically, because the
ideal concentrator term changes with FOV.

Figures 8 and 9 are the two compact W4C figures integrated at
`JOCN_Telemetry.tex:546-558`:

- `Figures/w4c_throughput_vs_load.pdf`: per-branch throughput versus offered
  load, with CPE averaging within runs and seed-level SD bars;
- `Figures/w4c_lifi_fov_response.pdf`: LiFi in-FOV and received-packet
  fractions for 40/70 degrees, with seed-level SD bars.

Both figures are generated from W4C analysis outputs and were visually
inspected in the rendered PDF on pages 12–13. No additional redundant delay,
jitter, or loss figure was added.

## 6. FlowMonitor wording

The manuscript uses **FlowMonitor-reported packet-loss ratio** for
`lostPackets/N_tx` at `JOCN_Telemetry.tex:515` and the limitation paragraph at
line 560. It explicitly states that this is not interpreted as terminal
packet loss at the finite simulation stop time and reports the W4C fact that
172/432 rows have `N_tx - N_rx != lostPackets`. No terminal-loss field was
created or reported.

## 7. Reviewer-response consistency

`MajorRevision/W2_wireless_ns3_reviewer_response.md` was replaced with the
W4C wireless response.

### Reviewer 3 Comment 4

The response begins by acknowledging that a successful build/run cannot
detect a plausible but incorrectly configured scenario, KPI extractor, or
flow mapping. It then gives the new evidence: final backend qualification,
9/9 independent LiFi tests, 15/15 compiled/reference checks, integrated
3+3+3 flow mapping with 9/9 five-tuple matches, byte-identical same-seed
outputs, and the complete 48-configuration/432-application-flow sweep.
The conclusion is bounded to reproducibility and internal consistency under
the declared ns-3 and optical-model assumptions; it does not claim physical
validation or calibration.

### Reviewer 3 Comment 3

The response separates LLM workflow evaluation from generated-data
validation. It claims scenario construction, technology-class coverage,
configuration coverage, repeatability, LiFi equation checking, mapping, and
full-sweep completion only. It explicitly does not invent unavailable token,
cost, latency, prompt, provider, or model-version logs.

### Reviewer 3 Comment 10

The response consistently uses ns-3, 5G NR/5G-LENA, Wi-Fi 6/IEEE 802.11ax,
and equation-driven LOS LiFi/OWC. Legacy LTE/EPC, 802.11n, and CSMA-surrogate
terms are scoped to the preserved legacy baseline rather than the W4C final
backend.

## 8. Stale-language and limitation audit

The active final claim path contains no legacy LTE/EPC, 802.11n, or
CSMA-surrogate final-result claim. The only remaining occurrence in the
manuscript is inside the excluded `comment` environment at
`JOCN_Telemetry.tex:563-570`, where it is now explicitly introduced as the
“preserved legacy/development ns-3 wireless use case.” The reviewer response
also scopes those terms explicitly to the legacy baseline. This preserves the
historical record without allowing it to be mistaken for W4C.

The single active wireless limitations paragraph at
`JOCN_Telemetry.tex:560` covers: NR model scope, Wi-Fi 802.11ax modelling
scope, uncalibrated equation-driven LiFi/OWC scope, configuration-specific
comparisons, practical-versus-synthetic separation, and FlowMonitor loss
semantics.

## 9. Build and visual verification

Commands executed in `/tmp/jocn-w0-github`:

```text
latexmk -pdf -interaction=nonstopmode -file-line-error JOCN_Telemetry.tex
pdftoppm -png -r 140 -f 10 -l 14 JOCN_Telemetry.pdf /tmp/pdfs/jocn-w4d-page
```

The PDF was generated as a 14-page, 612 x 792 pt document. The new wireless
content, Table 4, and Figures 8–9 are present and visually readable. The
source passes `git diff --check`.

`latexmk` returns nonzero because the pre-existing `sample.bib` contains
duplicate keys and existing unescaped ampersands (reported, for example, in
the generated `.bbl` at lines 13 and 146). These are unrelated to the W4D
wireless integration and were not repaired, consistent with the scope
instruction. The only bibliography additions made for the new LiFi
equations are the related Kahn/Barry and Komine/Nakagawa entries.

No new simulation was run in W4D. No practical measured data, semantic
experiment, optical experiment, or legacy sweep output was modified. No
commit or push was performed.

## 10. Further wireless work

No further wireless experiment is required for the W4D manuscript
integration. Any future work would be optional model calibration or broader
scenario validation, not a prerequisite for the bounded W4C claims. The
remaining action before a globally clean submission build is repair of the
pre-existing bibliography file, outside this focused wireless pass.

W4D_VERDICT=PASS_W4D_WIRELESS_INTEGRATION_WITH_KNOWN_PREEXISTING_BIBLIOGRAPHY_BLOCKER
FINAL_SYNTHETIC_BACKEND=ns-3.44_CTTC_5G-LENA_v4.0.y_NATIVE_WIFI_802.11ax_EQUATION_DRIVEN_LOS_LIFI_OWC
LEGACY_BACKEND_STATUS=UNCHANGED_AND_EXPLICITLY_SCOPED_AS_LEGACY_DEVELOPMENT_BASELINE
PRACTICAL_WIRELESS_STATUS=SEPARATE_MEASURED_5G_NR_WIFI6_LIFI_CAMPAIGN_NOT_CALIBRATED_BY_W4C
FINAL_SWEEP_INTEGRATED=YES_W4C
FINAL_DATASET_COUNTS=48_CONFIGURATIONS_432_APPLICATION_ROWS_144_PER_BRANCH_624_RAW_FLOWMONITOR_ROWS
LIFI_MODEL_WORDING=UNCALIBRATED_EQUATION_DRIVEN_LOS_LIFI_OWC_MODEL_WITH_STOCK_PACKET_ACCESS_ABSTRACTION_NOT_COMPLETE_PHYSICAL_PHY_MAC
TABLE4_STATUS=UPDATED_TO_W4C_SIX_EVIDENCE_ROWS_AND_VISUALLY_VERIFIED
FINAL_FIGURES=FIGURE_8_THROUGHPUT_VS_LOAD_AND_FIGURE_9_LIFI_FOV_RESPONSE
R3C4_RESPONSE_UPDATED=YES_WITH_W4C_CORRECTNESS_AND_REPRODUCIBILITY_EVIDENCE
R3C3_RESPONSE_UPDATED=YES_SIMULATION_SIDE_ONLY_NO_HISTORICAL_LLM_LOGS_INVENTED
R3C10_RESPONSE_UPDATED=YES_FINAL_TERMINOLOGY_LOCKED
STALE_LEGACY_LANGUAGE_REMOVED=YES_FROM_ACTIVE_CLAIM_PATH_AND_SCOPED_IN_ARCHIVAL_COMMENT_AND_RESPONSE
UNIVERSAL_RANKING_CLAIM=NOT_SUPPORTED_AND_NOT_MADE
PRACTICAL_CALIBRATION_CLAIM=NOT_SUPPORTED_AND_NOT_MADE
LATEX_BUILD_STATUS=PDF_GENERATED_AND_VISUALLY_CHECKED_BUT_STRICT_LATEXMK_BLOCKED_BY_PREEXISTING_NONWIRELESS_BIBLIOGRAPHY_ERRORS
READY_FOR_WIRELESS_FINAL_CLOSURE=YES_WIRELESS_CONTENT_CLOSED_WITH_BIBLIOGRAPHY_CLEANUP_OUTSTANDING
