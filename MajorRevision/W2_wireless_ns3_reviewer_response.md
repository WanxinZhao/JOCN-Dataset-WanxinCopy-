# Wireless synthetic-data reviewer response

## Reviewer 3, Comment 4 — Independent correctness validation

We agree that successful compilation and execution alone cannot establish the
correctness of generated simulation data. We therefore added independent
validation for the released ns-3 dataset. Across all 48 archived runs, an
independent parser reconstructed 624 FlowMonitor rows and the 432 explicitly
mapped application-flow records. All application-flow packet counters agreed
exactly with the exported KPI files. The maximum absolute differences caused
by XML time serialisation were 5.57 × 10^-5 Mbps for throughput,
3.16 × 10^-3 ms for mean delay, and 1.10 × 10^-5 ms for
mean jitter.

Three representative low-, medium-, and high-load configurations were then
rebuilt and replayed with ns-3.44. All three executed successfully, reproduced
the expected nine application flows, and gave zero KPI delta relative to the
archived results. Two executions of the same fixed-seed configuration also
produced identical application-flow KPIs. Finally, a separately written stock
ns-3 reference implementation passed all five topology/configuration checks
and all 63 keyed KPI comparisons.

These checks support the correctness and reproducibility of the released data
under the declared simulation assumptions. They are not a validation of
physical fidelity. The simulated branches are LTE/EPC, Wi-Fi 802.11n, and a
CSMA-based LiFi surrogate; the latter is not a physical LiFi channel model.
Loss is reported as the FlowMonitor-reported ratio
`lostPackets/txPackets`, not as terminal packet loss at the finite simulation
stop.

## Reviewer 3, Comment 3 — Simulation-side workflow evidence

The wireless demonstration covers 48 bounded configurations and 432
application-flow records. It establishes that the workflow can construct and
execute the declared heterogeneous ns-3 scenarios, export mapped per-flow
data, and reproduce representative configurations. The validation above
supports simulator-output and KPI-pipeline correctness; it does not establish
that an LLM workflow is superior to a deterministic or hand-written workflow.
The manuscript treats the LLM component as a feasibility demonstration and
reports its available trace information separately.

## Reviewer 3, Comment 10 — ns-3 terminology

The manuscript consistently uses `ns-3` and identifies the simulated access
branches as LTE/EPC, Wi-Fi 802.11n, and a CSMA-based LiFi surrogate. These
synthetic models are kept distinct from the separately measured practical
5G NR, Wi-Fi 6, and LiFi testbed. No claim is made that the simulation
reproduces or calibrates that practical testbed.

## Reviewer 1 — Synthetic wireless dataset summary

The dataset summary now reports ns-3, 48 run-level configurations, 432
application-flow records, 624 raw FlowMonitor rows, three seeds, four offered
loads, two mobility speeds, two LiFi-surrogate link rates, 1024-byte packets,
and 10-s runs. The released source, scenario metadata, FlowMonitor XML, KPI
CSV, and aggregate table are available under `NS3_Wireless/` in the cited
public data-generation repository. The independent reconstruction, replay,
repeatability, and reference-implementation evidence is released under
`MajorRevision/ns3_wireless_validation/` in the revision repository.

## Claim boundary

The dataset demonstrates bounded synthetic wireless data generation and
implementation-level reproducibility. Cross-branch differences are reported
only under the adopted configuration. The results do not establish a universal
technology ranking, 5G NR behaviour, a physical LiFi model, or calibration to
the practical wireless campaign.
