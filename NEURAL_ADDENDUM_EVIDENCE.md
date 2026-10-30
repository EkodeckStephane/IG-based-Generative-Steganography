# Independent neural revalidation — evidence and interpretation

Evidence folder: https://drive.google.com/drive/folders/1_KRB0gml1IfvoW3uKOmGKchYugNYK51C

Protocol: `neural-revalidation-residualcnn-v1`. This is a **new, distinct ResidualCNN v1**, not the original ResNet-18, with five fixed high-pass kernels on the generated lower image half, training-fold normalization, inner-validation model selection, 500 paired sources and five grouped folds.

| Detector / track | Positive-control macro AUC | Controlled Discop macro AUC | Interpretation |
| --- | ---: | ---: | --- |
| Historical ResNet-18 | 0.54156 | 0.52278 | Health gate failed (<0.8); original scientific-readiness flag remains false |
| Independent ResidualCNN v1 | 0.99028 | 0.50477 | Health gate passed; Discop 95% pair-bootstrap AUC interval [0.470878,0.5381715] |
| Historical SRM/FLD | 0.98407 | 0.46119 | Positive-control health gate passed |

ResidualCNN positive-control pair-bootstrap 95% interval: [0.9835965,0.996022]. Health-gate success checks responsiveness to this specified perturbation, **not** steganographic undetectability. The addendum does **not** evaluate the Fisher–Rao/NG-Stego method. Do not conflate the matched MNIST-VAE benchmark, native upstream experiments, original controlled campaign, and neural addendum.

Sources within the evidence folder: `SCIENTIFIC_REPORT.md`, `summary.json`, `protocol.json`, `validation_report.json`.