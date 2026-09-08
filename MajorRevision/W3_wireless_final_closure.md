# W3 wireless ns-3 final closure

## 1. Final scientific verdict

**PASS_WIRELESS_REVISION_CLOSED_WITH_KNOWN_LIMITATIONS**.

The active wireless-simulation text and the W2 reviewer response are now
consistent with the authoritative W1 report. The evidence supports a narrow
claim: the LLM-driven workflow constructed and executed bounded ns-3.44
scenarios and exported synthetic telemetry whose application-flow extraction,
configuration mapping, representative replay, fixed-seed repeatability, and
separately written reference implementation were checked. It does not support
physical-model validation, calibrated emulation of the measured testbed, a 5G
NR claim, a physical LiFi claim, or a universal access-technology ranking.

No simulation was run during W3. Optical and semantic-fusion experiments were
not changed. The W1 report remains the scientific source of truth:
`/home/ubuntu/Desktop/LLM Driven wireless environment generation/WIRELESS_REVISION_W1_NS3_VALIDATION.md`.

## 2. Manuscript consistency status

**PASS after minimal evidence-required corrections.** The active manuscript
locations are:

- `JOCN_Telemetry.tex:344`: the synthetic wireless DT row is explicitly marked
  `(generated)` and is separate from the measured `Wireless access` row.
- `JOCN_Telemetry.tex:497-538`: the wireless method, KPI definitions, four
  validation checks, Table 4, configuration-specific interpretation, and
  consolidated scope/limitations paragraph.
- `JOCN_Telemetry.tex:552`: the active conclusion uses the bounded ns-3
  correctness/reproducibility claim.

The W1 anchors are represented correctly: ns-3.44; 48 run configurations; 624
raw FlowMonitor rows; 432 application-flow rows; loads 2/5/10/20 Mbps;
mobility 0.5/3 m/s; CSMA-based LiFi-surrogate rates 50/100 Mbps; seeds 1/2/3;
1024-byte packets; 10-s simulation; three representative replays with nine
application flows each; identical same-seed KPIs; five reference checks and 63
KPI comparisons, all CONSISTENT.

The practical wireless description of the physical testbed still uses its
actual 5G New Radio/Wi-Fi 6/LiFi terminology. This is intentional and is now
clearly separated from the synthetic ns-3 branches; it is not a simulation
terminology error.

## 3. Table 4 status

**PASS.** `tab:ns3_validation` contains four distinct evidence layers:

| Table 4 row | Correct interpretation | W1 result |
|---|---|---|
| Full FlowMonitor reconstruction | Extraction and data-processing correctness | 48 runs; 624 raw and 432 application flows; counters exact; continuous application KPIs agree within XML serialization precision |
| Representative replay | Executable reproducibility of archived configurations | 3/3 configurations; nine application flows per run; zero archived-versus-replay KPI delta |
| Same-seed repeatability | Deterministic repeatability under the fixed build, seed, and configuration | Two executions of one medium configuration; identical application-flow KPIs |
| Independent ns-3 reference | Implementation consistency under the declared scenario assumptions | 5/5 topology/configuration checks and 63/63 KPI comparisons CONSISTENT; observed numerical delta 0 |

The table footnote and surrounding paragraph explicitly state that these are
implementation/data-generation checks, not physical-model validation.

## 4. Reviewer 3 Comment 4 response status

**PASS.** `MajorRevision/W2_wireless_ns3_reviewer_response.md:3-15`
acknowledges the specific concern that successful build/run checks alone cannot
detect plausible but incorrect simulation outputs. It presents evidence in the
requested order:

1. independent FlowMonitor recomputation for all 48 archived runs;
2. end-to-end scenario, source-parameter, FlowMonitor, KPI, and aggregate
   mapping consistency;
3. three representative replays;
4. same-seed repeatability;
5. the separately written hand-written ns-3 reference.

The numerical evidence is included rather than summarized only as “validation
added”: counters are exact; the maximum application discrepancies are
`5.56977e-5 Mbps` throughput, `0.00316445 ms` delay, and `1.10013e-5 ms`
jitter, with maximum relative discrepancy `6.31775e-6`; 3/3 replays have zero
delta; the fixed-seed repeat has identical KPIs; and all 63 reference checks
are CONSISTENT. The response also records the 50 delay rows beyond the initial
`1e-4 ms` screen and the larger control-flow timestamp sensitivity, so it does
not overstate bitwise equality.

Its final claim is bounded to correctness and reproducibility under the
declared ns-3 scenario assumptions. It does not claim that the simulator
results are physically validated.

## 5. Reviewer 3 Comment 3 simulation-response status

**PASS for the simulation-side scope.** `W2_wireless_ns3_reviewer_response.md:17-25`
separates LLM workflow evaluation from simulator/data validation. It supports
coverage, executable scenario construction, replayability, repeatability, and
KPI/mapping correctness. It does not invent unavailable LLM token counts,
API cost, latency, prompt, provider, or model-version history. It does not
claim an LLM advantage over deterministic scenario generation or unrestricted
scenario generalization.

## 6. Reviewer 3 Comment 10 terminology status

**PASS.** Active synthetic text and the response use:

- `ns-3` and `ns-3.44`;
- `LTE/EPC`;
- `Wi-Fi 802.11n`;
- `CSMA-based LiFi surrogate`.

The active synthetic text does not describe LTE/EPC as 5G NR, does not present
Wi-Fi 802.11n as the measured Wi-Fi 6 setup, and does not present the surrogate
as physical LiFi. The practical testbed paragraph retains its actual physical
technology names and explicitly identifies the separate measured campaign.

## 7. Remaining wireless limitations

The following limitations remain intentionally visible and are not blockers
for the narrowed revision claim:

- The cellular branch is LTE/EPC, not 5G NR.
- The simulated radio branch is Wi-Fi 802.11n, not calibrated emulation of the
  practical Wi-Fi 6 system.
- The LiFi branch is an idealized CSMA-based LiFi surrogate. It has no optical
  LOS/FOV geometry, photodiode response, optical modulation, shot noise,
  blockage, or calibrated optical channel/error model.
- Cross-branch throughput, delay, jitter, and loss differences are properties
  of the adopted topology, helper/channel assumptions, rates, delays, offered
  loads, mobility, and surrogate model; they are not universal technology
  rankings.
- `lostPackets/txPackets` is a FlowMonitor-reported packet-loss ratio. Because
  traffic reaches the 10-s stopping time, it is not interpreted as terminal
  packet loss; W1 found `lostPackets != txPackets-rxPackets` for all 432
  application flows.
- Replay and deterministic-repeatability evidence is bounded to the tested
  ns-3.44 build and fixed configurations. The hand-written reference shares
  stock ns-3 libraries and declared modelling assumptions.
- The archive contains stale base JSON/default values for some expanded
  parameters. The effective command-line parameters recorded for each run are
  the reproducibility source of truth; running the source without those
  overrides is not equivalent to replaying the archived variant.

## 8. Corrections made in W3

Only the following evidence-required corrections were made after the W2 pass:

1. Changed the validation prose from “three levels” to four complementary
   checks and stated their distinct interpretations.
2. Added a Table 4 note distinguishing extraction correctness, replay,
   fixed-seed repeatability, and independent implementation consistency from
   physical fidelity.
3. Marked the dataset-table entry as `Synthetic wireless DT (generated)`.
4. Consolidated the active wireless scope/limitations paragraph to include
   LTE/EPC versus 5G NR, Wi-Fi 802.11n versus calibrated Wi-Fi 6 emulation,
   the CSMA-based LiFi surrogate boundary, configuration-specific comparisons,
   and the FlowMonitor loss interpretation.
5. Corrected the W2 response opening and closing so the R3C4 answer explicitly
   addresses plausible-but-incorrect outputs and ends with the bounded
   correctness/reproducibility claim.
6. Corrected the loss wording to identify `lostPackets/N_tx`, rather than the
   `lostPackets` count alone, as the FlowMonitor-reported packet-loss ratio.

No bibliography entry was edited. No raw data, simulation artifact, or
semantic/optical experiment was overwritten.

## 9. Further wireless experiment requirement

**No further wireless experiment is required for the current manuscript claim.**
The W1 evidence already covers the complete archived KPI extraction, full
structural mapping, three representative replays, same-seed repeatability, and
independent reference implementation.

A new experiment would become necessary only if the manuscript were expanded
to claim terminal packet loss, physical LiFi fidelity, calibrated reproduction
of the measured wireless testbed, 5G NR simulation, or cross-platform
determinism. Those claims are explicitly excluded in the closed revision.

## Evidence index

Authoritative evidence directory:
`/home/ubuntu/Desktop/LLM Driven wireless environment generation/W1_NS3_VALIDATION/`.

Primary files used for this closure:

- `kpi_recomputation_summary.json` and `kpi_recomputation_comparison.csv`;
- `flowmonitor_recomputed.csv`;
- `sweep_consistency_summary.json` and `sweep_consistency.csv`;
- `replay_results.csv` and `replay_report.md`;
- `repeatability.csv` and `seed_sensitivity.csv`;
- `independent_reference/comparison.csv` and `independent_reference/report.md`;
- `ns3_claim_boundary.md` and `sweep_sanity_report.md`.

No new W3 simulation output was created.

## Final status

```text
W3_WIRELESS_VERDICT=PASS_WIRELESS_REVISION_CLOSED_WITH_KNOWN_LIMITATIONS
MANUSCRIPT_EVIDENCE_CONSISTENCY=PASS_AFTER_MINIMAL_CORRECTIONS
TABLE4_VALIDATION_STATUS=PASS_FOUR_DISTINCT_IMPLEMENTATION_EVIDENCE_LAYERS
R3C4_RESPONSE_STATUS=PASS_ORDERED_NUMERICAL_INDEPENDENT_CORRECTNESS_RESPONSE
R3C3_SIMULATION_RESPONSE_STATUS=PASS_SIMULATION_SIDE_ONLY_NO_INVENTED_LLM_HISTORY
R3C10_TERMINOLOGY_STATUS=PASS_TERMINOLOGY_LOCKED
FLOWMONITOR_LOSS_STATUS=PASS_REPORTED_RATIO_NOT_TERMINAL_LOSS
PRACTICAL_SYNTHETIC_SEPARATION=PASS_EXPLICIT
FURTHER_WIRELESS_EXPERIMENT_REQUIRED=NO_FOR_CURRENT_CLAIM_BOUNDARY
REMAINING_WIRELESS_LIMITATIONS=LTE_EPC_NOT_5G_NR; WIFI_80211N_NOT_WIFI6_EMULATION; CSMA_LIFI_SURROGATE_NOT_PHYSICAL; CONFIGURATION_SPECIFIC; CUTOFF_LOSS; FIXED_BUILD_SCOPE; STALE_BASE_DEFAULTS
```
