# A07 — Experimental comparison scope (Version 1.0)

The revised manuscript separates three distinct evidence tracks:

1. **Matched S5 MNIST-VAE carrier:** common-channel comparison of Euclidean/Fisher-preconditioned path coding and iMEC/Discop channel adapters. Its reported detection metrics are conditional on this fixed generator and payload protocol.
2. **Native upstream coding studies:** GPT-2/WikiText-103 iMEC text and Transformer-XL/IMDb and ImageGPT/CelebA Discop experiments. These represent different native generators and datasets and are not the same-carrier NG-Stego benchmark.
3. **Controlled Discop neural addendum:** 500 source-paired images with an independent ResidualCNN v1 and a passed positive-control gate. Its detector AUC characterizes controlled Discop pairs, not NG-Stego and not the historical ResNet-18.

**Reporting rule:** No cross-track pooling or ranking of AUCs, because sources, carriers, datasets, payloads, features and detector protocols differ. The positive-control AUC is a detector-health diagnostic, not a steganography security score.

Source evidence: [native campaign folder](https://drive.google.com/drive/folders/1xr3gYO8QTm7MoCLRVxFmfAMjzZr4PGhu), [neural addendum folder](https://drive.google.com/drive/folders/1_KRB0gml1IfvoW3uKOmGKchYugNYK51C), `REMOTE_CAMPAIGN_MANIFEST.json` and `NEURAL_ADDENDUM_EVIDENCE.md`.
