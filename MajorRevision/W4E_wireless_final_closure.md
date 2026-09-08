# W4E final wireless closure

## 1. Final scientific verdict

**Verdict: `PASS_WIRELESS_FINAL_CLOSED_WITH_KNOWN_LIMITATIONS`.**

The active manuscript and wireless reviewer response faithfully represent the
final W4C synthetic wireless experiment. The final evidence path is the
ns-3.44 implementation with CTTC 5G-LENA `5g-lena-v4.0.y`, native Wi-Fi
802.11ax, and an equation-driven LOS LiFi/OWC model. The final sweep is
48 configurations and 432 application-flow records, with 144 records per
branch and 624 raw FlowMonitor records. The manuscript preserves the
measured practical wireless campaign as a separate evidence track.

No new simulation, regeneration, sweep expansion, optical work, semantic
work, or LiFi redesign was performed in W4E. No material manuscript or
reviewer-response correction was required after the consistency audit.

The known limitation is build-system-only: the temporary PDF is generated and
visually checked, but strict `latexmk` remains nonzero because of pre-existing
duplicate BibTeX entries and unescaped ampersands in unrelated `sample.bib`
entries. Those bibliography defects were intentionally not repaired in this
wireless closure.

## 2. Active-text evidence audit

The active manuscript was checked against the W4B implementation report, W4C
final sweep report, and W4D integration report. The relevant active locations
are:

| Location | Consistency result |
|---|---|
| `JOCN_Telemetry.tex:97` | Contribution identifies the final 5G NR, Wi-Fi 6/802.11ax, and equation-driven LOS LiFi/OWC synthetic scenario. |
| `JOCN_Telemetry.tex:339-344` | Dataset table separates practical measured wireless data from the synthetic three-RAT DT row. |
| `JOCN_Telemetry.tex:497-512` | Final W4C backend, topology, parameters, workload, FOV sweep, counts, and LiFi equations. |
| `JOCN_Telemetry.tex:514-515` | KPI formulas and FlowMonitor loss boundary. |
| `JOCN_Telemetry.tex:517-520` | Final W4B/W4C correctness, mapping, repeatability, and sweep evidence. |
| `JOCN_Telemetry.tex:522-542` | Current Table 4. |
| `JOCN_Telemetry.tex:544-560` | W4C result effects, Figures 8–9, and one consolidated limitation paragraph. |
| `JOCN_Telemetry.tex:572-574` | Active conclusion uses W4C rather than the legacy backend. |
| `MajorRevision/W2_wireless_ns3_reviewer_response.md:5-46` | Current wireless responses and claim boundaries. |

The active final synthetic claim path contains no statement that LTE/EPC,
802.11n, or a CSMA-only link is the W4C final backend. The remaining legacy
terms in `JOCN_Telemetry.tex:563-570` are inside the excluded `comment`
environment and are explicitly introduced as the preserved
legacy/development wireless use case. The response similarly scopes those
terms to the legacy baseline.

The abstract has no stale legacy synthetic claim and no calibration or
physical-fidelity overclaim. It remains a high-level summary of the overall
dataset and GNPy/semantic contributions; no change was made because the
minimum-change instruction did not require adding new abstract content.

## 3. Final numerical consistency

All stated W4C numerical anchors in the active wireless text and response
match `WIRELESS_REVISION_W4C_FINAL_SWEEP.md`:

| Quantity | Final value | Status |
|---|---:|---|
| ns-3 | 3.44 | MATCH |
| Offered loads | 2, 5, 10, 20 Mbps | MATCH |
| Mobility speeds | 0.5, 3 m/s | MATCH |
| LiFi receiver FOV | 40°, 70° | MATCH |
| Seeds | 1, 2, 3 | MATCH |
| Simulation duration | 10 s | MATCH |
| Packet size | 1024 bytes | MATCH |
| Run configurations | 48 | MATCH |
| Application flows per run | 3 NR + 3 Wi-Fi + 3 LiFi = 9 | MATCH |
| Application-flow records | 432 | MATCH |
| Per-branch records | 144 NR, 144 Wi-Fi, 144 LiFi | MATCH with W4C; totals are represented in manuscript/response context |
| Raw FlowMonitor rows | 624 | MATCH |
| Final flow mappings | 432/432 PASS | MATCH |

The W4C result values reproduced in `JOCN_Telemetry.tex:544` also match the
authoritative report: load contrasts of 18.486 Mbps for NR, 0.151 Mbps for
Wi-Fi, and 15.726 Mbps for LiFi; Wi-Fi delay increase of 1,653.88 ms and
FlowMonitor-reported loss-ratio increase of 0.701; mobility throughput
changes of 0, 0.00018, and -2.572 Mbps for NR, Wi-Fi, and LiFi; and matched
FOV reductions of 0.299 in both in-FOV and received-packet fractions.

These figures are presented as run-level, configuration-specific effects.
They are not universal RAT rankings.

## 4. LiFi model boundary

The manuscript consistently calls the final branch an **equation-driven LOS
LiFi/OWC model**. At `JOCN_Telemetry.tex:504-510`, it identifies Lambertian
emission, geometry, receiver FOV, received optical power, responsivity,
shot/thermal noise, SNR, OOK BER, and PER. It also retains the important
implementation boundary: a stock point-to-point packet path is the IP/UDP
access abstraction, so this is not a complete standardized LiFi PHY/MAC and
is not calibrated to the practical testbed.

No active text calls it a complete LiFi PHY/MAC, calibrated emulator, measured
LiFi model, or full optical-room multipath model. The limitation is stated in
the method and once in the consolidated wireless-scope paragraph, without
being expanded into repetitive or contradictory caveats.

## 5. Practical-versus-synthetic boundary

The practical measured wireless campaign is described at
`JOCN_Telemetry.tex:379-381` as telemetry from a physical multi-access
platform containing 5G NR, Wi-Fi 6, and LiFi. The synthetic W4C experiment is
described at `JOCN_Telemetry.tex:500-512` as separate generated data using
5G-LENA NR, native 802.11ax, and equation-driven LOS LiFi/OWC.

The text explicitly states that the shared technology classes do not imply
calibrated emulation, reproduction of measured values, or validation of the
physical testbed. This satisfies the required two-dataset distinction.

## 6. W4C result interpretation

The load, mobility, and FOV discussion at `JOCN_Telemetry.tex:544` is within
the W4C claim boundary:

- Wi-Fi queueing response and NR/LiFi throughput response are described under
  the adopted configuration;
- mobility is described as a small configuration-specific NR/Wi-Fi effect
  and a LiFi geometry effect;
- 40° versus 70° is described through reduced in-FOV and received-packet
  fractions;
- the concentrator-gain interaction is acknowledged, so no unsupported
  monotonic aggregate SNR/power claim is made;
- no branch is said to universally outperform another.

The active text does not claim that NR is universally better, LiFi is
universally superior, or Wi-Fi is intrinsically worse.

## 7. FlowMonitor loss boundary

At `JOCN_Telemetry.tex:515` and line 560, loss is named the
**FlowMonitor-reported packet-loss ratio** and defined as
`lostPackets/N_tx`. The manuscript explicitly says it is not terminal packet
loss at the finite stopping time and records the W4C observation that 172 of
432 rows have `N_tx-N_rx` different from the FlowMonitor field. No terminal
loss variable is introduced. The reviewer response repeats the same boundary
at lines 16 and 46.

## 8. Table 4 status

Table 4 at `JOCN_Telemetry.tex:522-542` is based on W4B/W4C evidence, not the
legacy W1 LTE/EPC/802.11n sweep. It contains all required evidence types:

1. NR/Wi-Fi backend qualification;
2. 9/9 independent LiFi equation tests;
3. 15/15 compiled ns-3 versus independent Python comparisons;
4. integrated three-RAT mapping with 9/9 mapped application flows;
5. byte-identical same-seed repeatability;
6. 48/48 W4C completion and 432/432 mapping passes.

The table footnote separates implementation/equation/mapping/repeatability
evidence from physical-model validation. It does not conflate correctness,
repeatability, reproducibility, or physical fidelity.

## 9. Figures 8 and 9

Figure 8 at `JOCN_Telemetry.tex:546-551` uses
`Figures/w4c_throughput_vs_load.pdf`. Its caption identifies final W4C
synthetic wireless throughput, branch labels, CPE averaging within runs, and
seed-level standard deviations. It contains no legacy labels or universal
ranking claim.

Figure 9 at `JOCN_Telemetry.tex:553-558` uses
`Figures/w4c_lifi_fov_response.pdf`. Its caption identifies the final LiFi/OWC
FOV response, in-FOV and received-packet fractions, and seed-level variation.
It contains no legacy labels or physical-calibration claim.

The text and cross-references are correct: Table 4 is referenced from the
validation paragraph, Figure 8 and Figure 9 are present in the rendered PDF,
and no missing wireless figure reference was found.

## 10. Reviewer-response status

### R3 Comment 4

`W2_wireless_ns3_reviewer_response.md:5-18` explicitly acknowledges that
successful build/run checks alone cannot detect a plausible but incorrect
configuration, KPI extractor, or flow mapping. It then reports the final
independent evidence: 9/9 LiFi equation tests, 15/15 compiled-versus-Python
checks, integrated 3+3+3 branch mapping with 9/9 matches, byte-identical
same-seed outputs, and 48/48 final runs with 432/432 mappings. The conclusion
is limited to internal correctness and reproducibility under declared model
assumptions; it does not claim physical-testbed validation.

### R3 Comment 3

`W2_wireless_ns3_reviewer_response.md:20-26` describes the final three-RAT
workflow and bounded 48-configuration evaluation. It distinguishes LLM
workflow evaluation from simulator/data validation and explicitly does not
invent historical token, cost, latency, prompt, provider, or model-version
logs.

### R3 Comment 10

`W2_wireless_ns3_reviewer_response.md:28-36` uses the final terminology:
5G NR with CTTC 5G-LENA on ns-3.44, Wi-Fi 6/IEEE 802.11ax, and an
equation-driven LOS LiFi/OWC model. It no longer presents unsupported-NR,
802.11n, or CSMA-only wording as the final experiment; those terms are
explicitly legacy-only.

## 11. Build and visual check

The latest preview command was:

```text
latexmk -pdf -interaction=nonstopmode -file-line-error JOCN_Telemetry.tex
```

It generated `JOCN_Telemetry.pdf` with 14 pages. Wireless pages 11–13 were
rendered with `pdftoppm` and visually inspected. Table 4, Figure 8, Figure 9,
captions, page transitions, and the limitation paragraph are readable with
no wireless-induced clipping or overlap. The source passes `git diff --check`.

The nonzero `latexmk` status is caused by existing `sample.bib` duplicate
entries and unescaped ampersands reported in the generated `.bbl` (including
lines 13 and 146). No unrelated bibliography cleanup was performed.

## 12. Further wireless work

No further wireless experiment is required. W4C is the final bounded
synthetic wireless experiment, and W4E confirms that its evidence is
consistently represented in the manuscript and response. Remaining
limitations are intentionally scientific rather than unresolved closure
defects: the synthetic stack is uncalibrated to the practical testbed, the
LiFi implementation is an equation-driven LOS model behind a stock packet
access abstraction rather than a complete PHY/MAC, cross-RAT results are
configuration-specific, and FlowMonitor `lostPackets` is not terminal loss.

W4E_VERDICT=PASS_WIRELESS_FINAL_CLOSED_WITH_KNOWN_LIMITATIONS
FINAL_BACKEND_CONSISTENCY=PASS_W4C_NS3_44_5GLENA_NATIVE_WIFI_80211AX_EQUATION_DRIVEN_LOS_LIFI_OWC
FINAL_DATASET_COUNTS=48_CONFIGURATIONS_432_APPLICATION_ROWS_144_NR_144_WIFI_144_LIFI_624_RAW_FLOWMONITOR_ROWS
PRACTICAL_SYNTHETIC_BOUNDARY=PASS_SEPARATE_MEASURED_5G_NR_WIFI6_LIFI_AND_UNCALIBRATED_SYNTHETIC_W4C_DATASET
LEGACY_BASELINE_SCOPE=PASS_LEGACY_TERMS_EXPLICITLY_SCOPED_OUTSIDE_ACTIVE_W4C_CLAIM_PATH
TABLE4_STATUS=PASS_CURRENT_W4B_W4C_EVIDENCE_NOT_LEGACY_SWEEP
FIGURE8_STATUS=PASS_FINAL_W4C_THROUGHPUT_FIGURE
FIGURE9_STATUS=PASS_FINAL_W4C_LIFI_FOV_FIGURE
R3C3_STATUS=PASS_FINAL_THREE_RAT_SIMULATION_SIDE_ONLY_NO_HISTORICAL_LLM_LOGS_INVENTED
R3C4_STATUS=PASS_FINAL_INDEPENDENT_CORRECTNESS_AND_REPRODUCIBILITY_EVIDENCE
R3C10_STATUS=PASS_NS_3_5G_NR_WIFI_802_11AX_EQUATION_DRIVEN_LOS_LIFI_OWC_TERMINOLOGY
LIFI_CLAIM_BOUNDARY=PASS_EQUATION_DRIVEN_LOS_UNCALIBRATED_STOCK_PACKET_ACCESS_NOT_COMPLETE_PHYSICAL_LIFI_PHY_MAC
FLOWMONITOR_LOSS_BOUNDARY=PASS_FLOWMONITOR_REPORTED_PACKET_LOSS_NOT_TERMINAL_PACKET_LOSS
UNIVERSAL_RANKING_CLAIM=NO_UNSUPPORTED_CLAIM_PRESENT
PRACTICAL_CALIBRATION_CLAIM=NO_UNSUPPORTED_CLAIM_PRESENT
FURTHER_WIRELESS_EXPERIMENT_REQUIRED=NO
WIRELESS_LINE_STATUS=CLOSED_FINAL_W4C_EVIDENCE_CONSISTENT
BIBLIOGRAPHY_BLOCKER_STATUS=PREEXISTING_DUPLICATE_KEYS_AND_UNESCAPED_AMPERSANDS_NOT_REPAIRED_PER_SCOPE
