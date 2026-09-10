# Dataset provenance and exclusions

## BOSSBase 1.01

BOSSBase is used locally for natural-image development, calibration and frozen evaluation splits. Raw BOSSBase images are intentionally **not redistributed in this repository**.

The current working archive was checked as 10,000 grayscale PGM `P5` images, 512×512, 8 bit. The frozen filename-based split is retained in `results/bossbase_split_manifest_v4.csv`.

## BOWS2

BOWS2 is reserved as the primary external validation dataset. The validation protocol was frozen before corpus access. At the time of this snapshot, the raw BOWS2 corpus had not yet been supplied to the working environment and no replacement dataset was silently substituted.

## Generated stego images

Generated V7/V8 stego images are intentionally excluded from Git history because they are bulky derived artifacts. Numerical summaries, seeds/protocols and reproducible runners are retained instead.
