# E3: Deterministic baseline and public-evidence audit

## Completed

- Generated the complete 6,144-configuration ground-truth set with a deterministic enumerator.
- Compared the published multi-agent scenario set against the deterministic set.
- Measured missing, extra and duplicate configurations.
- Audited the two published iterations and their launch powers.

## Cannot be truthfully rerun from the available repository

The public repository does not provide the agent/orchestrator source code, system prompts, tool schemas, model snapshot, API settings, per-call logs, token usage, latency, cost, retry trace, or human-intervention trace. Consequently, single-LLM, no-reflection and repeated full multi-agent trials cannot be reconstructed from the artifacts alone.

The corresponding fields are recorded as `not_reported` rather than inferred or fabricated. A complete E3 requires the original agent implementation and its runtime credentials/logging instrumentation.

## Published reflection evidence

The published report contains one two-iteration run. Iteration 1 executes 2,048 cases at -5.5 dBm. Iteration 2 executes 6,144 cases at -5.5, -5.0 and -4.5 dBm, which repeats all 2,048 first-iteration configurations. This is execution history, not 8,192 unique dataset configurations.
