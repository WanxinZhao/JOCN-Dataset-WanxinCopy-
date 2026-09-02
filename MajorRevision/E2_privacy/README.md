# E2: Multi-attacker privacy experiment

This directory is produced by `MajorRevision/run_e1_e2.py` using the same chronological split as E1.

Dominant CPE is the primary privacy target. Dominant RAT is diagnostic only because Wi-Fi accounts for approximately 98.6% of all records in the full dataset. Accuracy on RAT must not be interpreted without the majority baseline.

The table below reports the strongest observed CPE attacker for each representation; lower Macro-F1 means less observed leakage.

| representation    | attacker         |   macro_f1_mean |   macro_f1_ci95 |
|:------------------|:-----------------|----------------:|----------------:|
| PCA3              | RandomForest     |        0.217447 |     0.00594841  |
| RandomProjection3 | GradientBoosting |        0.224618 |     0.0115722   |
| RawPrivate        | GradientBoosting |        0.275721 |     0           |
| V1                | GradientBoosting |        0.248086 |     1.81336e-17 |
| V2                | GradientBoosting |        0.246891 |     0.010202    |
| V3_8D_sigma005    | GradientBoosting |        0.243532 |     0.0117371   |
| V3_sigma0         | GradientBoosting |        0.24471  |     0.0075889   |
| V3_sigma001       | GradientBoosting |        0.23662  |     0.0121646   |
| V3_sigma005       | GradientBoosting |        0.238168 |     0.0112742   |
| V3_sigma010       | GradientBoosting |        0.231894 |     0.0123135   |
