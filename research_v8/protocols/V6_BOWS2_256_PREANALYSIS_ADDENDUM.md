# V6 BOWS2 256×256 External Confirmation — Pre-analysis Addendum

**Status: FROZEN AFTER ARCHIVE/HEADER QUALIFICATION AND BEFORE ANY V6 PIXEL-STATISTIC ANALYSIS.**  
Date: 2026-09-19.

This addendum supplements, and does not rewrite, `BOSSBASE_V6_PMF_GEOMETRY_PREREG.md` and `V6_BOWS2_EXTERNAL_PREREG_ADDENDUM.md`. The earlier documents expected a 10,000-image 512×512 BOWS2 corpus. The supplied corpus has now been qualified as a 10,000-image native 256×256 PGM corpus. The dimensional discrepancy is recorded before any V6 residual/stratum/PMF statistic is computed from BOWS2.

## 1. Corpus qualification

The user supplied the two split-archive volumes:

- `BOWS2_split.z01`
- `BOWS2_split.zip`

They were reunified into `BOWS2_full.zip` without image conversion.

Integrity and header qualification:

- split part SHA-256 `BOWS2_split.z01`: `d71ad881d8922c8759473162fa15ddb1c00cd66dd93740e94eda56daeffc7f3b`;
- split part SHA-256 `BOWS2_split.zip`: `8f36c9fc4a2e3c087477e866024a43fde9182037795a092ccf3875ff18d1dc2f`;
- reunified ZIP SHA-256: `5e017969c09e8e1ed98205ce2155e96ffa56dbfe056693075726c3b0b0f3b316`;
- full ZIP integrity test: PASS;
- PGM count: exactly 10,000;
- all 10,000 PGM headers: `P5`, width 256, height 256, `maxval=255`;
- header anomalies: 0.

Header inspection is treated only as corpus qualification. No BOWS2 V6 residual distribution, stratum frequency, Fisher coordinate, candidate risk, or iso-Cachin result was computed before this addendum was frozen.

## 2. Declared dimensional deviation

The only protocol-level corpus deviation is the native image size:

- earlier frozen expectation: 512×512;
- supplied qualified corpus: 256×256.

The external analysis therefore uses the supplied images **at native 256×256 resolution**. No resize, upsampling, padding, interpolation, re-encoding, denoising, enhancement, or synthetic 512×512 conversion is permitted.

Changing the native image dimensions changes the number of lattice sites per image and may change the observed external source distribution. Those effects are part of the external-source test and must be reported rather than normalized away by image transformation.

## 3. Frozen V6 objects retained unchanged

The following objects and rules remain exactly frozen:

- exact Cachin orientation `D_KL(P_C || P_S)`;
- non-overlapping 3×3 center-carrier lattice;
- eligibility rule `0 < center < 255`;
- four-neighbor rounded predictor;
- eight BOSSBase-fit context strata and integer `cut_vnum` thresholds;
- residual support `{-255,...,255}`;
- Jeffreys smoothing `alpha=0.5`;
- frozen BOSSBase `p0` and `w0`;
- frozen Fisher shape basis `V/H`, with `K=3`;
- `r_shape = 0.2375032471006036`;
- security budgets `{2e-4, 8e-4}`;
- the 128 already-frozen nominal iso-Cachin designs per budget;
- the final independently 131072-direction-certified uniform-shrink and V6-robust candidates;
- direct empirical BOWS2 weighting by `w_ext`, with frozen-`w0` risk reported only secondarily;
- all geometry-transfer diagnostics and decision thresholds from the earlier external addendum.

No object above may be refitted or rescaled because the BOWS2 images are 256×256.

## 4. External extraction at native resolution

For each 256×256 image, apply the unchanged 3×3 lattice definition to the native pixel grid. Use the unchanged eligibility rule, context statistic, frozen stratum assignment, predictor, and integer residual. Accumulate the complete external counts over all 10,000 images.

The external PMFs remain

`p_ext,g(k) = (n_gk + 0.5)/(n_g + 0.5*511)`

and the external stratum masses remain

`w_ext,g = n_g / sum_h n_h`.

All risk values remain expressed per eligible residual under the same V6 definitions. No target image-size correction factor is introduced.

## 5. Frozen external endpoints

The external evaluation remains exactly the one defined previously:

1. corpus integrity and duplicate-file reporting;
2. external stratum masses and PMFs;
3. Fisher geometry transfer diagnostics:
   - projected norm `||delta_ext||`;
   - full whitened norm `||z_ext||`;
   - normalized orthogonal residual;
   - stratum-mass TV mismatch;
4. direct empirical BOWS2 Cachin risk for each frozen uniform-shrink and robust candidate;
5. secondary frozen-`w0` risk;
6. external iso-Cachin risk distribution for all 128 frozen designs per budget;
7. `D80 = Q90 - Q10` with the unchanged materiality rule.

## 6. Decision vocabulary retained

The earlier four-way decision vocabulary remains unchanged:

- **IN-MANIFOLD EXTERNAL PASS**;
- **OUT-OF-MANIFOLD / PHENOMENON CONFIRMED**;
- **IN-MANIFOLD SECURITY NOT CONFIRMED**;
- **EXTERNAL PHENOMENON NOT CONFIRMED**.

The image-size deviation creates no new favorable outcome category and does not relax any threshold.

## 7. Prohibited post-hoc actions

After this addendum, no adjustment is permitted to the predictor, lattice, strata, support, smoothing, `p0`, `w0`, Fisher basis, `K`, radius, epsilon values, candidate beta vectors, iso-Cachin design vectors, risk orientation, weighting rule, materiality threshold, or external decision rule based on BOWS2 outcomes.

The 256×256 resolution is therefore treated as a documented external-source property, not as a reason to alter the frozen V6 model.
