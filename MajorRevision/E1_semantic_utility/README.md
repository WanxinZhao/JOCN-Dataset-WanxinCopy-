# E1: Leakage-free temporal semantic-utility experiment

This directory is produced by `MajorRevision/run_e1_e2.py`.

Important interpretation: the optical and wireless campaigns do not overlap in time. The sequence mapping is retained only as a constructed data-interoperability benchmark; it is not a contemporaneous end-to-end measurement.

All scalers, semantic thresholds, optical risk thresholds, encoders and downstream models are fitted after the chronological split. Ten records are purged at each boundary. The four-class result is exploratory if the final test block contains too few samples of class 3.

## Top binary results

| method               | task   |   runs |   accuracy_mean |   accuracy_std |   accuracy_ci95 |   balanced_accuracy_mean |   balanced_accuracy_std |   balanced_accuracy_ci95 |   macro_f1_mean |   macro_f1_std |   macro_f1_ci95 |   auroc_mean |   auroc_std |   auroc_ci95 |   auprc_mean |   auprc_std |   auprc_ci95 |
|:---------------------|:-------|-------:|----------------:|---------------:|----------------:|-------------------------:|------------------------:|-------------------------:|----------------:|---------------:|----------------:|-------------:|------------:|-------------:|-------------:|------------:|-------------:|
| V3NoNoisePlusOptical | binary |     10 |        0.775263 |     0.00456365 |      0.00282858 |                 0.634443 |              0.00770197 |               0.00477373 |        0.64733  |     0.006844   |      0.00424195 |     0.698725 |  0.00632587 |   0.00392082 |     0.447375 |  0.00706368 |   0.00437811 |
| V3PlusOptical        | binary |     10 |        0.773333 |     0.00854682 |      0.00529737 |                 0.633182 |              0.00853424 |               0.00528958 |        0.645662 |     0.00868864 |      0.00538528 |     0.698304 |  0.00461978 |   0.00286337 |     0.447853 |  0.0109778  |   0.00680413 |
| V1PlusOptical        | binary |     10 |        0.765965 |     0.00322434 |      0.00199847 |                 0.635602 |              0.00663878 |               0.00411476 |        0.645522 |     0.00649    |      0.00402254 |     0.702987 |  0.00355649 |   0.00220434 |     0.440238 |  0.00882711 |   0.0054711  |
| V3_8DPlusOptical     | binary |     10 |        0.761404 |     0.0107831  |      0.00668343 |                 0.630811 |              0.00790564 |               0.00489997 |        0.639923 |     0.00901165 |      0.00558548 |     0.700503 |  0.0117403  |   0.00727669 |     0.435608 |  0.0185964  |   0.0115262  |
| V2PlusOptical        | binary |     10 |        0.756667 |     0.0138647  |      0.00859343 |                 0.629782 |              0.0060566  |               0.00375392 |        0.637401 |     0.00704866 |      0.00436881 |     0.695343 |  0.0112769  |   0.00698951 |     0.430335 |  0.0103862  |   0.00643743 |

Runtime: 425.9 s.
