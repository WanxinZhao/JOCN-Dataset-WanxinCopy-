# Representative replay report

Each replay compiled the exact archived `generated.cc` for the selected run with `/usr/bin/c++` and the existing ns-3.44 build libraries, then executed it with the archived parameter values. The simulator was run from the workspace with a relative output directory because the installed CommandLine path handling did not accept an absolute path containing spaces. The parameter values are unchanged.

| Replay | Archive run | Compile rc | Run rc | Application flows | Max abs throughput delta | Max abs loss delta | Max abs delay delta | Max abs jitter delta |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| high_load_high_mobility | 20260619T104709Z-hybrid-seed3-t10p0-l20p0-s3p0 | 0 | 0 | 9 | 0 | 0 | 0 | 0 |
| low_load_low_mobility | 20260619T103518Z-hybrid-seed1-t10p0-l2p0-s0p5 | 0 | 0 | 9 | 0 | 0 | 0 | 0 |
| medium_load_high_mobility | 20260619T104328Z-hybrid-seed2-t10p0-l10p0-s3p0 | 0 | 0 | 9 | 0 | 0 | 0 | 0 |

All three replays built and executed successfully and produced nine classifier-identified application flows. All listed numerical deltas are zero under the independent XML parser. The full per-flow values are in `replay_results.csv`; commands and logs are below each replay directory.

## Commands

```text
W1_NS3_VALIDATION/replays/low_load_low_mobility/archived_generated_rebuilt --outputDir=W1_NS3_VALIDATION/replays/low_load_low_mobility/fresh_results --simTime=10.0 --seed=1 --offeredLoadMbps=2 --packetSize=1024 --mobilitySpeed=0.5 --lifiRateMbps=50
W1_NS3_VALIDATION/replays/medium_load_high_mobility/archived_generated_rebuilt --outputDir=W1_NS3_VALIDATION/replays/medium_load_high_mobility/fresh_results --simTime=10.0 --seed=2 --offeredLoadMbps=10 --packetSize=1024 --mobilitySpeed=3 --lifiRateMbps=100
W1_NS3_VALIDATION/replays/high_load_high_mobility/archived_generated_rebuilt --outputDir=W1_NS3_VALIDATION/replays/high_load_high_mobility/fresh_results --simTime=10.0 --seed=3 --offeredLoadMbps=20 --packetSize=1024 --mobilitySpeed=3 --lifiRateMbps=100
```

The exact compile command for each source is recorded in its `compile.log`; run stdout/stderr and command are recorded in its `run.log`.
