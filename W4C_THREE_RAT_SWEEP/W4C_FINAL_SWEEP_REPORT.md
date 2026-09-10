# W4C final bounded three-RAT synthetic wireless sweep

## 1. Executive verdict

**Verdict: `PASS_W4C_WITH_LIMITATIONS`.**

The final source generated all requested 48 run configurations using ns-3.44, CTTC 5G-LENA `5g-lena-v4.0.y`, native `WIFI_STANDARD_80211ax`, and the equation-driven LOS LiFi/OWC implementation. The frozen sweep contains 432 application-flow records: 144 NR, 144 Wi-Fi 802.11ax, and 144 LiFi. Every run produced the expected nine application flows, all 9/9 five-tuple/interface mappings passed, all required KPI values were finite, and no application-key duplicates or missing configurations were found.

The LiFi branch is physically grounded at the LOS link-budget/error-decision level and passed independent equation checks. It is nevertheless an **uncalibrated equation-driven LOS OWC model behind a stock packet-access abstraction**, not a complete standardized LiFi PHY/MAC and not a calibrated model of the practical optical/wireless testbed. All KPI comparisons are therefore configuration-specific and are not technology rankings.

Evidence level: the structural and numerical statements below are **OBSERVED** in the W4C outputs or source. Interpretations about load, mobility, and FOV effects are **INFERRED from the bounded sweep** and are explicitly not generalized beyond the adopted configuration. Practical-testbed calibration is **MISSING**.

No manuscript, practical measured data, semantic-fusion experiment, or legacy sweep output was modified. The final 48-run sweep was run once; no larger sweep was launched.

## 2. Final source and execution environment

### 2.1 Source of record

The final project-local W4C source is:

- `W4C_THREE_RAT_SWEEP/ns3/three_rat_smoke.cc`
- `W4C_THREE_RAT_SWEEP/ns3/lifi_owc.h`
- `W4C_THREE_RAT_SWEEP/ns3/lifi_owc_impl.inc`
- `W4C_THREE_RAT_SWEEP/ns3/lifi_owc.cc`

The executable source uses the project-local implementation include at `three_rat_smoke.cc:35-38`; no W4B absolute source include is required. The small `.cc` wrapper at `lifi_owc.cc:1-2` includes the local implementation file. The W4C source remains separate from the validated legacy project.

### 2.2 Build/runtime information

Observed execution information:

| Item | Value | Evidence |
|---|---|---|
| ns-3 | 3.44 | `/tmp/w4a-ns3-EEnH/ns-3.44/VERSION`; `three_rat_smoke.cc:337-342` |
| NR backend | CTTC 5G-LENA `5g-lena-v4.0.y` | `three_rat_smoke.cc:340`; W4A-qualified environment |
| Qualified 5G-LENA revision | `2c0ed9740e677224bdfff4eab5aea5adcd8f6052` | W4A authoritative report |
| Build root | `/tmp/w4a-ns3-EEnH/ns-3.44` | W4C execution record |
| Binary | `/tmp/w4a-ns3-EEnH/ns-3.44/build/scratch/ns3.44-three_rat_smoke` | W4C sweep command/status |
| Build profile | CMake `release`, C++20 | ns-3 CMake cache in the qualified build root |
| Compiler | g++ 15.2.0 | `/usr/bin/g++ --version` |
| Build command | `/home/ubuntu/.local/bin/python3.12 ns3 build -j 4 three_rat_smoke` | W4C execution record |

The direct compiled binary was used for execution. The ns-3 Python wrapper was not needed for the simulation runs.

## 3. Final three-RAT implementation

### 3.1 NR branch

The integrated source creates three CPE/UE nodes and one gNB, installs `NrHelper`/EPC, and configures the `InH-OfficeOpen` 3GPP channel at `3.5e9` Hz, 40 MHz, numerology 1, and 30 dBm gNB power (`three_rat_smoke.cc:428-475`). The branch is therefore **5G NR using CTTC 5G-LENA**, not LTE/EPC. The NR application flows are installed at `three_rat_smoke.cc:490-507`.

The synthetic NR parameters are representative and uncalibrated to the practical testbed unless explicitly documented elsewhere; no equivalence to a measured 5G NR deployment is claimed.

### 3.2 Wi-Fi branch

The source explicitly sets `WIFI_STANDARD_80211ax`, `ConstantRateWifiManager` with `HeMcs0`, a 5 GHz 20 MHz channel, and fixed 16 dBm transmit power (`three_rat_smoke.cc:509-527`). One AP and three mobile CPE stations are used. UDP downlink application flows are installed at `three_rat_smoke.cc:532-548`.

This is **Wi-Fi 802.11ax** in the synthetic simulation. It is not a calibrated reproduction of the practical testbed's Wi-Fi 6 deployment; the practical and synthetic datasets must remain distinct.

### 3.3 Equation-driven LiFi/OWC branch

The LiFi branch uses one fixed optical AP/transmitter and three mobile CPE receivers. A stock point-to-point packet path is used as the IP/UDP access abstraction, while receive corruption is decided by the optical error model (`three_rat_smoke.cc:138-193`). The source comments explicitly state that this is not a standardized LiFi PHY/MAC (`three_rat_smoke.cc:4-9`).

The implementation computes the following at `lifi_owc_impl.inc:54-114`:

\[
m=-\frac{\ln 2}{\ln(\cos\Phi_{half})},
\]

\[
H_{LOS}=\frac{(m+1)A}{2\pi d^2}\cos^m(\phi)T_sg(\psi)\cos(\psi),
\]

within the receiver FOV and with nonnegative irradiance angle, with `H_LOS=0` otherwise; `g(psi)=n^2/sin^2(Psi_c)`. It then computes `P_r`, signal current, shot and thermal noise, SNR, `BER=Q(sqrt(SNR)/2)`, and `PER=1-(1-BER)^(8L)`. Packet corruption uses the PER and an explicitly assigned ns-3 random stream at `lifi_owc_impl.inc:201-234`.

All fixed physical parameters are exposed by the command line and written into every `run_config.csv` (`three_rat_smoke.cc:604-681` and `324-368`): 10 W optical power, 60° half-power semi-angle, `1e-4 m^2` detector area, 0.5 A/W responsivity, 40° or 70° receiver FOV, refractive index 1.5, filter gain 1, 5.1 µA background current, 300 kHz bandwidth, 295 K, 1 MΩ load resistance, 1024-byte packets, 100 Mbps nominal packet-link rate, downward transmitter and upward receiver orientations. These parameters are explicit and **uncalibrated** to the practical testbed.

The optical-state exporter writes time, CPE, distance, irradiance/incidence angles, FOV state, Lambertian order, channel gain, received power, signal/noise terms, SNR, BER, PER, and packet counters (`lifi_owc_impl.inc:117-151`).

## 4. FOV preflight and frozen sweep design

### 4.1 Preflight

The preflight used load 5 Mbps, speed 0.5 m/s, seed 1, the final geometry, 10 s simulation, and the 1.0–9.5 s application window. The output is `W4C_THREE_RAT_SWEEP/preflight/fov_preflight_summary.csv`, with the interpretation in `preflight/fov_preflight_report.md`.

| FOV | In-FOV fraction | Zero-gain fraction | Received-packet fraction | Median received power (W) | Median SNR | Median BER | Median PER |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 30° | 0.638889 | 0.361111 | 0.638139 | 4.46944e-4 | 2.27229e9 | 0 | 0 |
| 40° | 0.876984 | 0.123016 | 0.873876 | 2.70432e-4 | 1.35497e9 | 0 | 0 |
| 50° | 1.000000 | 0.000000 | 1.000000 | 1.90408e-4 | 9.39528e8 | 0 | 0 |
| 70° | 1.000000 | 0.000000 | 1.000000 | 1.26538e-4 | 6.08609e8 | 0 | 0 |

**Selected narrow FOV: 40°.** This provides measurable out-of-FOV states while retaining approximately 0.874 received-packet fraction in the preflight; 30° is closer to outage and 50° produces no out-of-FOV states under this geometry. The selection was based on the physical-state/packet evidence, not on favorable branch ranking. The selected value was frozen before the 48-run sweep.

### 4.2 Sweep grid and workload

The final grid is exactly:

| Factor | Values |
|---|---|
| Offered load | 2, 5, 10, 20 Mbps |
| CPE mobility speed | 0.5, 3.0 m/s |
| LiFi receiver FOV | 40°, 70° |
| Random seed | 1, 2, 3 |
| Simulation duration | 10 s |
| Application window | 1.0–9.5 s |
| Packet size | 1024 bytes |

Thus `4 × 2 × 2 × 3 = 48` run configurations. Each run uses the same offered-load target, packet size, application window, seed, and common mobile CPE state for all three branches. The branch-specific UDP interval is computed from the common offered load and packet size at `three_rat_smoke.cc:180-188`, `498-504`, and `539-545`.

The sweep command was:

```text
/home/ubuntu/.local/bin/python3.12 W4C_THREE_RAT_SWEEP/run_w4c_sweep.py \
  --binary=/tmp/w4a-ns3-EEnH/ns-3.44/build/scratch/ns3.44-three_rat_smoke \
  --output-root=/tmp/w4c-canonical/runs \
  --status-file=W4C_THREE_RAT_SWEEP/sweep_status.csv
```

The runner froze each result under `W4C_THREE_RAT_SWEEP/runs/<run-key>/` and did not overwrite existing run directories. The status file contains 48 PASS rows, zero nonzero return codes, and 48 matched-flow counts of 9. Total recorded execution time was approximately 226.49 s; this is not a scientific KPI.

### 4.3 Final-source acceptance run

Before the sweep, the final source was run at load 5 Mbps, speed 0.5 m/s, FOV 40°, seed 1, with the declared 10 s/1.0–9.5 s timing. `final_runs/acceptance_integrated/` contains 9 application KPI rows, 9/9 matched mappings, populated `optical_state.csv`, and the expected three rows for each of NR, Wi-Fi 802.11ax, and LiFi. No required KPI was nonfinite. The independent final-source link probe in `final_runs/acceptance_probe/` was compared against the Python reference with 15/15 PASS values. The same-seed duplicate check is documented in Section 7.

## 5. Final dataset and structural checks

### 5.1 Output inventory

| Artifact | Observed coverage | Scientific role |
|---|---:|---|
| `runs/*/run_config.csv` | 48 | Per-run factor values, backend labels, timing, and LiFi parameters |
| `runs/*/scenario_metadata.csv` | 48 × 9 rows | Declared branch/CPE/five-tuple metadata |
| `runs/*/flow_mapping.csv` | 48 × 9 rows | FlowMonitor-to-declared-flow and interface mapping |
| `runs/*/flowmon.xml` | 48 × 13 raw flow rows | Raw FlowMonitor exports, including non-application/control flows |
| `runs/*/kpi.csv` | 48 × 9 application rows | Exported application-flow KPIs |
| `runs/*/optical_state.csv` | 48 files; 252 or 255 rows/run | Sampled LiFi physical intermediate states |
| `analysis/final_application_flow_dataset.csv` | 432 rows | Final application-flow table, one row per run × branch × CPE |
| `analysis/final_dataset_summary.csv` | 48 rows | One-row-per-run structural summary |
| `analysis/grouped_kpi_summary.csv` | 48 factor cells | CPE-averaged run means and three-seed standard deviations |
| `analysis/lifi_physical_summary.csv` | 144 rows | One row per LiFi run × CPE physical-state summary |

The raw XML has 13 flows/run, or 624 rows total. The KPI exporter deliberately filters to the nine declared application five-tuples and excludes infrastructure/control flows at `three_rat_smoke.cc:227-238`. Therefore the final application table has 432 rows, not 624.

### 5.2 Structural result

`analysis/sweep_structure_summary.json` and `analysis/sweep_structure_report.md` report:

- 48/48 run configurations observed;
- 432/432 application rows observed;
- 144 NR rows, 144 Wi-Fi 802.11ax rows, and 144 LiFi rows;
- exactly 3 rows per branch and 9 application rows per run;
- 624 raw FlowMonitor rows, 13 per run;
- zero duplicate application keys;
- all required KPI values finite;
- all per-run mapping checks PASS.

An independent metadata/KPI/mapping tuple comparison found no mismatched or missing five-tuples in any of the 48 runs. Required numeric fields in both KPI and optical-state files contained no NaN or Inf values. These checks were performed by `aggregate_w4c.py` and by the additional metadata/KPI/mapping comparison recorded during W4C.

The final application dataset retains `FlowMonitor_lostPackets` and `FlowMonitor_reported_loss_ratio`; it does not create a terminal-loss field from `tx_packets-rx_packets`.

## 6. Flow mapping and common-state validation

The mapping function matches declared application flows by the complete IPv4 five-tuple, not by FlowId alone (`three_rat_smoke.cc:257-321`). It then checks the expected device class:

- NR: remote-host point-to-point source to `NrUeNetDevice` destination;
- Wi-Fi 802.11ax: `WifiNetDevice` to `WifiNetDevice`;
- LiFi: point-to-point packet-access abstraction to point-to-point packet-access abstraction, with the optical error model attached to the receiver path.

The final acceptance output at `final_runs/acceptance_integrated/flow_mapping.csv` contains 9/9 `MATCHED,PASS` rows: 3 NR, 3 Wi-Fi 802.11ax, and 3 LiFi. The 48-run structural audit repeats this check for all 432 application rows. The integrated scenario creates the three branch interfaces and distinct IP subnets before writing metadata (`three_rat_smoke.cc:429-555`).

The three branches share the same three mobile CPE nodes and the same `RandomWalk2dMobilityModel` realization within each run (`three_rat_smoke.cc:106-126` and `428-440`). They use the common workload values through the three application-installation blocks cited above. This supports a common-workload, configuration-specific comparison; it does not make the branches physically equivalent.

## 7. Same-seed repeatability

The final source was executed twice with the identical configuration: offered load 5 Mbps, speed 0.5 m/s, FOV 40°, seed 1, run 1, 10 s simulation, and 1.0–9.5 s application window. The resulting directories are `final_runs/repeat_a/` and `final_runs/repeat_b/`. The two runs were compared byte-for-byte for `run_config.csv`, `scenario_metadata.csv`, `flow_mapping.csv`, `kpi.csv`, `flowmon.xml`, and `optical_state.csv`; all six files were exactly equal. Both runs contained 9 application KPI rows and 252 optical-state rows. This is an observed deterministic repeatability result for the fixed ns-3.44 build, seed, run number, and configuration, not a claim about all environments.

The direct command template was:

```text
/tmp/w4a-ns3-EEnH/ns-3.44/build/scratch/ns3.44-three_rat_smoke \
  --mode=integrated --outputDir=<repeat-output-directory> \
  --simTime=10s --appStart=1s --appStop=9.5s \
  --offeredMbps=5 --speed=0.5 --fovDeg=40 --seed=1 --run=1
```

Two initial duplicate invocations were aborted before simulation because their newly named output directories had not yet been created; the logger could not open `optical_state.csv`. After creating the isolated directories, both actual repeat executions completed successfully and produced the exact-equality result above. This setup failure did not enter the 48-run sweep; `sweep_status.csv` records 48/48 PASS.

## 8. LiFi validation and physical-response analysis

### 7.1 Independent equation tests

The independent Python test suite is `W4C_THREE_RAT_SWEEP/lifi_validation/lifi_reference.py` and `run_lifi_unit_tests.py`; it does not call the C++ implementation. The report `lifi_unit_test_report.md` records **9/9 PASS** for Lambertian order, aligned LOS gain, inverse-square behavior, FOV gate, received power, finite zero-power noise/SNR, monotonic PER, and BER/PER bounds.

The independent probe comparison is `lifi_validation/lifi_reference_comparison.csv`. It compares aligned-near, aligned-far, and out-of-FOV geometries and records **15/15 PASS** values with zero absolute and relative difference at exported precision for `H_LOS`, received power, SNR, BER, and PER.

### 7.2 FOV response in the final sweep

The analysis output is `analysis/lifi_fov_paired_physical_contrasts.csv` and the interpretation is in `analysis/scientific_sweep_analysis.md`. Within matched load/speed/seed/CPE observations, 40° minus 70° produced the following means:

- in-FOV fraction: `-0.299306`;
- zero-gain fraction: `+0.299306`;
- received-packet fraction computed from exported tx/rx counters: `-0.299295` at the run level;
- mean BER: `+0.149653`;
- mean PER: `+0.299306`.

The mean `H_LOS`, received power, and SNR were **not** forced to decrease: their matched mean deltas were respectively `+9.26612e-6`, `+9.26612e-5 W`, and `+4.90029e8`. This is consistent with the implemented equation because narrowing the FOV both removes out-of-FOV states and increases the ideal concentrator gain `n²/sin²(Psi_c)` for states still inside the FOV (`lifi_owc_impl.inc:84-101`). Consequently, the correct scientific statement is that the narrow FOV reduces geometric acceptance and received-packet fraction while the accepted-link gain changes according to the explicit concentrator term; an aggregate received-power/SNR monotonicity claim would be unsupported.

The LiFi application FlowMonitor-reported loss ratio remains separate and is not interpreted as terminal packet loss. The FOV response is therefore evidenced by the optical states, received counters, and throughput, not by relabelling `tx-rx` as terminal loss.

## 9. Scientific sweep analysis

The analysis uses the run as the experimental unit. It first averages the three CPE application rows within each run/branch and then reports the three seeds as replicate observations for each fixed parameter cell. The main artifacts are:

- `analysis/run_level_kpi.csv`;
- `analysis/factor_main_effect_summary.csv`;
- `analysis/paired_factor_contrasts.csv`;
- `analysis/branch_variation_summary.csv`;
- `analysis/lifi_physical_grouped_summary_recomputed.csv`;
- `analysis/scientific_sweep_analysis.md`.

### Q1 — offered load

Paired 20−2 Mbps changes, averaging matched load contrasts over the nuisance factors, were:

| Branch | Throughput change (Mbps) | Mean delay change (ms) | Mean jitter change (ms) | FlowMonitor-reported loss-ratio change |
|---|---:|---:|---:|---:|
| NR | +18.4864 | +0.02650 | −0.00643 | 0 |
| Wi-Fi 802.11ax | +0.1511 | +1653.88 | +2.5591 | +0.70127 |
| LiFi | +15.7256 | approximately 0 | 0 | 0 |

**Observed/inferred conclusion:** under the adopted configuration, NR and LiFi throughput remain responsive to the increased offered workload, while Wi-Fi 802.11ax shows a strongly queueing/FlowMonitor-reported-loss-sensitive response. This supports a bounded statement about load-limited versus queueing-limited behavior in these configurations. It does not support a universal capacity ranking.

### Q2 — mobility

Paired 3.0−0.5 m/s changes across matched load/FOV/seed conditions were:

| Branch | Throughput change (Mbps) | Mean delay change (ms) | Mean jitter change (ms) | FlowMonitor-reported loss-ratio change |
|---|---:|---:|---:|---:|
| NR | 0 | +0.000594 | +0.000309 | 0 |
| Wi-Fi 802.11ax | +0.000182 | +0.07970 | +0.00219 | −0.000246 |
| LiFi | −2.5724 | −0.00937 | 0 | 0 |

**Observed/inferred conclusion:** mobility produces little change in NR and Wi-Fi throughput under this channel/traffic configuration, while the same movement changes the LiFi geometry and hence its received-throughput response. This is an empirical property of the selected channel, mobility, geometry, and seed set; it is not a claim that mobility is generally inert for NR or Wi-Fi.

### Q3 — LiFi FOV

The 40° FOV reduces in-FOV and received-packet fractions and increases the out-of-FOV BER/PER contribution. The accepted-state channel gain and SNR also reflect the compensating ideal concentrator gain, as described in Section 7.2. This is the expected behavior of the declared equation-driven model, not a calibrated physical-testbed result.

### Q4 — RAT-dependent variation

Across the 48 run-level branch observations, the branch distribution summary reports:

| Branch | Throughput mean ± SD (Mbps) | Delay mean ± SD (ms) | Jitter mean ± SD (ms) | FlowMonitor-reported loss-ratio mean ± SD |
|---|---:|---:|---:|---:|
| NR | 9.501 ± 7.092 | 2.539 ± 0.0116 | 0.1849 ± 0.0336 | 0 ± 0 |
| Wi-Fi 802.11ax | 2.168 ± 0.0662 | 1347.754 ± 880.583 | 3.215 ± 0.935 | 0.365 ± 0.252 |
| LiFi | 8.082 ± 6.620 | 0.07965 ± 0.0106 | 0 ± 0 | 0 ± 0 |

These nontrivial, branch-dependent distributions show that the final synthetic data contain more than a branch label. They must be interpreted only as results **under the adopted simulation configuration**. The differences depend on topology, helpers, channel settings, link rates/delays, offered load, mobility, and the LiFi surrogate abstraction.

### Q5 — effectively inert factors

The bounded analysis identifies several near-invariant outputs: NR throughput is exactly unchanged in the paired mobility contrast; Wi-Fi throughput mobility change is approximately zero; LiFi jitter and FlowMonitor-reported loss ratio are invariant in the current grid. These are reported as observed properties of this finite sweep, not as universal model conclusions. The LiFi FOV factor is not inert in the physical-state outputs.

## 10. FlowMonitor wording boundary

The exporter computes throughput, mean delay, mean jitter, and the FlowMonitor-reported ratio `lostPackets/txPackets` at `three_rat_smoke.cc:239-247`. The final dataset names this field `FlowMonitor_reported_loss_ratio` and retains the raw `FlowMonitor_lostPackets` field.

These fields are not called terminal packet loss. Because applications stop at 9.5 s and the simulation stops at 10 s, packet accounting at the stopping boundary can differ from `tx_packets-rx_packets`; no terminal-loss interpretation is made in this W4C analysis. This is why the final analysis uses the FlowMonitor field, throughput, received counters, and LiFi optical state separately.

## 11. Candidate analysis outputs

Three compact dependency-free SVG candidate figures were generated:

- `analysis/figures/throughput_vs_offered_load.svg`;
- `analysis/figures/delay_vs_offered_load.svg`;
- `analysis/figures/lifi_fov_physical_response.svg`.

They are analysis candidates only; no LaTeX or manuscript figure was edited in W4C. The proposed compact manuscript table is a parameter-sweep/dataset-coverage table with the following entries:

| Field | Final synthetic wireless DT value |
|---|---|
| Generator | ns-3.44 with CTTC 5G-LENA `5g-lena-v4.0.y` |
| Type | Synthetic/generated wireless DT data |
| Access branches | 5G NR; Wi-Fi 802.11ax; equation-driven LOS LiFi/OWC |
| Run configurations | 48 |
| Application-flow records | 432 |
| Raw FlowMonitor rows | 624 |
| Seeds | 1, 2, 3 |
| Offered load | 2/5/10/20 Mbps |
| Mobility | 0.5/3.0 m/s |
| LiFi receiver FOV | 40°/70° |
| Packet size | 1024 bytes |
| Simulation duration | 10 s |
| Outputs | FlowMonitor XML, per-flow KPI CSV, scenario metadata, flow mapping, optical-state CSV, aggregated CSV |
| Validation | Independent optical equation tests; full structural/KPI export audit; final-source repeatability check |

This row must be kept distinct from the measured practical wireless dataset. The W4C files contain generated ns-3 telemetry, not physical measurement records.

## 12. Legacy and practical-data boundary

The old LTE/EPC + Wi-Fi 802.11n + CSMA-surrogate sweep remains an unchanged legacy baseline under its existing project path. It was not numerically mixed with the W4C dataset and its W1 validation was not reused as validation of the new stack.

The final W4C dataset demonstrates configurable synthetic scenario construction and export for the access-technology classes of interest. It does not demonstrate that:

- the NR branch is equivalent to the practical testbed;
- the Wi-Fi 802.11ax branch is a calibrated reproduction of practical Wi-Fi 6;
- the equation-driven LOS LiFi/OWC branch is a physical standardized LiFi implementation;
- synthetic telemetry validates measured wireless telemetry;
- one access technology universally outperforms another.

The LiFi branch does not model optical phenomena beyond the implemented LOS/FOV link-budget geometry, and it has no photodetector dynamics beyond the declared responsivity/noise equations, optical modulation standard, calibrated shot/ambient model, blockage model, multipath model, or standardized LiFi PHY/MAC. Its packet-access layer is stock point-to-point. The model is therefore a bounded physical link/error abstraction, not a complete optical-wireless simulator.

## 13. W4C final status

W4C did not run a final sweep larger than 48 configurations and did not edit the manuscript. The final source is ready for manuscript integration only with the above claim boundaries and with the W4C evidence table/analysis artifacts cited as generated-data validation, not physical validation.

```text
W4C_VERDICT=PASS_W4C_WITH_LIMITATIONS
FINAL_SOURCE_STATUS=PASS_NS3_44_5GLENA_AX_EQUATION_DRIVEN_LOS_LIFI
FOV_PREFLIGHT=PASS_30_40_50_70_EVALUATED
NARROW_FOV_SELECTED=40_DEGREES
SWEEP_CONFIGURATIONS_EXPECTED=48
SWEEP_CONFIGURATIONS_COMPLETED=48
APPLICATION_ROWS_EXPECTED=432
APPLICATION_ROWS_OBSERVED=432
NR_ROWS=144
WIFI6_ROWS=144
LIFI_ROWS=144
FLOW_MAPPING_STATUS=PASS_432_OF_432
LIFI_PHYSICAL_RESPONSE_STATUS=PASS_FOV_GATE_AND_INDEPENDENT_EQUATION_CHECKS
SAME_WORKLOAD_ACROSS_RATS=YES_COMMON_LOAD_PACKET_SIZE_WINDOW_AND_CPE_MOBILITY
DATASET_STRUCTURAL_STATUS=PASS_NO_MISSING_DUPLICATE_OR_NONFINITE_REQUIRED_VALUES
OFFERED_LOAD_EFFECT=CONFIGURATION_SPECIFIC_WIFI_QUEUEING_RESPONSE_NR_AND_LIFI_THROUGHPUT_RESPONSE
MOBILITY_EFFECT=CONFIGURATION_SPECIFIC_SMALL_NR_WIFI_EFFECT_AND_LIFI_GEOMETRY_EFFECT
FOV_EFFECT=PASS_IN_FOV_AND_RECEIVED_PACKET_FRACTIONS_DECREASE_AT_40_DEGREES
UNIVERSAL_TECHNOLOGY_RANKING_SUPPORTED=NO
PRACTICAL_TESTBED_CALIBRATION=NO
LEGACY_DATASET_STATUS=UNCHANGED_BASELINE
READY_FOR_MANUSCRIPT_INTEGRATION=YES_WITH_BOUNDED_CLAIMS
```
