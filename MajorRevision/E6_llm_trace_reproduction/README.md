# E6: OpenAI trace reproduction

Current LLM scope: feasibility demonstration with the existing Agent architecture. Corrected E6 baseline, result figures, phase-specific API costs, runtime and manual recovery are documented in [../13_E6_demonstration_revision.md](../13_E6_demonstration_revision.md). The corrected unique data and figures are in the E6 `corrected_analysis/` directory; older power-sweep reports remain historical evidence.

## Purpose

This experiment reruns the recovered multi-agent workflow while preserving the
runtime-rendered API requests and complete OpenAI response objects. It is new
reproduction evidence and must not be described as the unavailable original
historical API trace.

## Reproduction configuration

- Provider for this new run: OpenAI. The authors separately confirm OpenAI as
  the historical provider, but the E6 trace is not evidence for the historical
  call sequence or exact model snapshot.
- Source implementation: [`WanxinZhao/ECOC2026_Code@57b04f1`](https://github.com/WanxinZhao/ECOC2026_Code/commit/57b04f1).
- Model requested for the new run: `gpt-4o-mini-2024-07-18` (fixed snapshot).
- Historical source model string: `gpt-4o-mini` (moving alias).
- Temperature: `0.2`.
- Timeout: `90 s`.
- Maximum attempts per provider: `3`.
- Strict LLM mode: enabled; an API failure cannot be hidden by a rule fallback.
- Topology: the audited `E5_recovered_gnpy_replay/source/NDFF_Testbed.json`.
- Equipment: the audited schema-fixed
  `E5_recovered_gnpy_replay/source/eqpt_config_NDFF_schema_fixed.json`.
- Pricing snapshot date: `2026-09-13`.
- Pricing per 1M text tokens: input `$0.15`, cached input `$0.075`, output `$0.60`,
  from the [official OpenAI GPT-4o mini model page](https://developers.openai.com/api/docs/models/gpt-4o-mini).

## Output layout

The local launcher writes every run to `runs/<run_id>/`. The `llm_trace`
subdirectory contains:

- `run_manifest.json`;
- `requests/*.json`;
- `responses/*.json`;
- `calls.jsonl`;
- `call_summary.csv`;
- `errors.jsonl` when an attempt fails.

The manifest also records the source commit and dirty state, Python and package
versions, input hashes, the exact user request, whether any API key was configured
(never the key itself), runtime settings, aggregate token use and estimated cost.

## Current completed reproduction

The new reproduction `20260913_134829_038619` is complete. It made six OpenAI
calls (six first-attempt successes, no retries or API failures) using the
returned model snapshot `gpt-4o-mini-2024-07-18`. The retained trace reports
108,308 total tokens, 26.22 s summed API latency, and an estimated text-token
cost of `$0.01726635`. Six rendered request objects, six complete response
objects, the call log, manifest, source/input hashes, generated records, and
raw GNPy runtime files are preserved in the public archive.

The authoritative persistent copy is
[`JOCN-DATASET-Code@553cbb1`](https://github.com/WanxinZhao/JOCN-DATASET-Code/tree/553cbb1a03cfcac2008ca21a067442eba0c84289/revision_experiments/E6_llm_trace_reproduction).
The archive is named
`E6_completed_reproduction_20260913_134829_038619.tar.gz` and has SHA-256
`d233ca08f2075084a75460a899b38ae36145349fad63db0d5056fe30ad2c7720`.
It is new reproduction evidence and does not reconstruct the unavailable
byte-exact historical trace.
