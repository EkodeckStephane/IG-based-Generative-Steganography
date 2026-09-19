# V7 operational screening closure

**Decision: GO TO STC**

V7 is a matched-ideal-payload development screening layer on 800 frozen fit/calibration images.

| epsilon | method | ideal bpp | change/eligible | PSNR dB | AUC |
|---:|---|---:|---:|---:|---:|
| 2e-4 | uniform_shrink | 0.058046 | 0.107950 | 67.421 | 0.505022 |
| 2e-4 | IG_matched | 0.058046 | 0.114292 | 67.173 | 0.502361 |
| 8e-4 | uniform_shrink | 0.078550 | 0.157984 | 65.767 | 0.508172 |
| 8e-4 | IG_matched | 0.078550 | 0.168414 | 65.489 | 0.502589 |

All four stochastic-realization checks pass. This screening layer validates image-domain realization and motivates actual-message coding plus strong detector-facing evaluation.
