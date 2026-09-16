# Major-revision evidence and experiments

The point-by-point reviewer response is maintained separately in
[`Response_Letter/response_letter.tex`](Response_Letter/response_letter.tex),
with a compiled review copy at
[`Response_Letter/response_letter.pdf`](Response_Letter/response_letter.pdf).

The released datasets, metadata, and associated documentation are covered by
the repository-level [CC BY-NC 4.0 data licence](../LICENSE).

Current LLM scope: feasibility demonstration with the existing Agent architecture. Corrected E6 baseline, result figures, phase-specific API costs, runtime and manual recovery are documented in [13_E6_demonstration_revision.md](13_E6_demonstration_revision.md). The corrected unique data and figures are in the E6 `corrected_analysis/` directory; older power-sweep reports remain historical evidence.

This directory contains the experiments, raw outputs, reproducibility files,
and reviewer-response evidence used for the JOCN major revision. The current
authoritative reviewer status is in
`W5C_complete_point_by_point_response.md`; facts that still require a data
owner are isolated in `W5C_author_confirmation_required.md`.

| ID | Evaluation | Main report | Reproducibility material | Current status |
|---|---|---|---|---|
| E1 | Semantic utility with chronological, leakage-controlled splits | `01_E1_语义效用实验结果.md` | `E1_semantic_utility/`, `run_e1_e2.py` | Complete, 10 seeds |
| E2 | Privacy--utility trade-off under several attackers | `02_E2_隐私泄露实验结果.md` | `E2_privacy/`, `run_e1_e2.py` | Complete, 10 seeds |
| E3 | LLM/multi-agent baseline and evidence audit | `03_E3_LLM基线实验结果.md` | `E3_llm_baseline/`, `run_e3_e4.py` | Observable evidence complete; historical per-call API traces unavailable |
| E4 | GNPy uniqueness, warning, and provenance audit | `04_E4_GNPy正确性实验结果.md` | `E4_gnpy_audit/`, `run_e3_e4.py` | Complete artifact audit |
| E5 | Recovered-source GNPy replay and strict-version comparison | `07_E5_恢复源码复现实验结果.md` | `E5_recovered_gnpy_replay/`, `run_e5_recovered_gnpy.py` | Complete; both arms 96/96 |
| E6 | OpenAI per-call trace reproduction | `E6_llm_trace_reproduction/README.md` | Public archive at `JOCN-DATASET-Code@553cbb1` | Complete new reproduction: 6/6 calls, exact requests/responses, 108,308 tokens |
| Wireless validation | Released synthetic ns-3 dataset validation | `W2_wireless_ns3_reviewer_response.md` | `ns3_wireless_validation/` and the simulator/data release in the cited workflow repository | Current manuscript evidence; 48 configurations and 432 application-flow records |
| Three-RAT dataset | Experimental three-RAT backend study | historical development reports | `synthetic_three_rat_wireless_dataset/` | Retained as development evidence; not used in the current manuscript claim path |

For E3, `E3_llm_baseline/prompt_inventory.md` records the author-confirmed
OpenAI provider, the three released prompt-template locations, the recovered
model/settings, and the exact boundary between source templates and unavailable
historical per-call API traces.

E6 adds a separately identified 2026-09-13 OpenAI reproduction with a fixed
model snapshot, per-call requests/responses, token usage, API latency, and
estimated cost. It improves prospective reproducibility but is not labelled as
the missing historical trace.

The release also includes:

- machine-readable Croissant 1.0 metadata in `croissant_metadata.json`;
- the materialised 2,848-row, 52-field leakage-controlled fusion table at
  `../semantic_case_v6/data/cross_domain_fusion_dataset.csv`, including source
  row indices, chronological split membership, and training-only thresholds;
- provenance for two distinct 339-km NDFF Voyager campaigns: the 2023--2024
  15-minute processed product and the Christmas 2025 raw eight-channel source.

Important interpretation boundaries:

- The optical and wireless traces were not measured contemporaneously. Their
  positional sequence mapping is an interoperability benchmark, not evidence
  of a shared physical incident.
- E1/E2 labels are deterministic next-record targets derived from the released
  variables. No incremental fusion-superiority claim is made.
- The pinned GNPy v2.12-compatible replay closely reproduces the released
  GSNR values; the larger GNPy 2.14.2 differences are reported as version/model
  sensitivity.
- The released ns-3 dataset validates reproducible bounded synthetic
  telemetry for LTE/EPC, Wi-Fi 802.11n, and a CSMA-based LiFi surrogate; it
  does not establish calibrated fidelity to the practical wireless testbed.
