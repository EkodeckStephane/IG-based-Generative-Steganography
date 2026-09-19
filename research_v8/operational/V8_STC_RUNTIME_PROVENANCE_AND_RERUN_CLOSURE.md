# V8 STC runtime provenance and clean-rerun closure

## Scope

This note closes the raw-evidence and runtime-reproducibility gap for the V8 actual-message STC experiment. It does **not** close detector-facing steganalysis; SRM+EC and the frozen deep-detector tier remain separate evidence requirements.

## Dependency provenance

The historical compiled `stc_extension*.so` binary used during the first V8 execution is no longer available with a recorded binary SHA-256. Therefore this closure does not claim binary identity.

The branch nevertheless contains the source-level reconstruction that was committed on 2026-09-10 immediately after the original execution, with commit messages explicitly tying the code to V8, including:

- `6f1e4b6e236c1ec31af594e44ffa3e7542d4fcab` — "Add V8 STC matrix subset used by frozen payloads";
- `878341a57c68dc6ad93970a5b149d23032e2de39` — "Add STC extraction source used by V8";
- `b3b5e3193e3a45f1e62dd727dd83c5853c2df108` — "Add STC Python extension interface used by V8";
- `9683084f2eb82dd166443528c9af0d9191be60d4` — "Add minimal multilayer STC implementation used by V8";
- `7228ecabfc5b72cd3c28b44e0ecbfd0c18d45d5e` — "Add STC embedding core used by V8";
- final attribution/test/build closure through `8179764a478dc63141c43ab9d3880b968f3992d1`.

The tracked package is `research_v8/vendor/pystc_minimal/`. It is a local source-level reconstruction of the pySTC low-level ±1 pathway and is **not** asserted to be byte-identical to any current upstream pySTC revision.

## Rebuild and low-level QA

The tracked source was rebuilt with:

- Python 3.13.5;
- g++ 14.2.0;
- Linux x86_64;
- C++11 build flags from the tracked `setup.py`.

Rebuilt extension SHA-256:

`b3c2e86ebb31a9b95ad8102588212889320221928b8deac4b211cdfd9bab9fcc`

The tracked `test_lowlevel.py` passed at rates 0.30, 0.48, and 0.64 with return codes 0/0 and BER = 0 in every case.

## Dataset and frozen V8 protocol

The split BOSSBase archive was rejoined and integrity-tested before the rerun.

Rejoined archive SHA-256:

`396be6f36f8c183312d7223b745fcffb5748606c3c8ec79579f7c5703143e9b4`

The frozen V4 split manifest was used. Only the 3500 `fit` and 1500 `calibration` images were included; the holdout remained excluded. The frozen V8 target rates, deterministic SHA-256 message generation, carrier lattice, strata, and `uniform_shrink` / `IG_matched` designs were unchanged.

## Clean full rerun

A clean rerun was performed for all 5000 non-holdout images under four conditions, yielding 20,000 fresh image-condition records. Every final raw record contains a direct STC execution return code; no cached-image-only record remains in the final lineage.

Results:

| epsilon | method | successes / 5000 | failures | bit errors on successful encodings |
|---|---|---:|---:|---:|
| 2e-4 | uniform_shrink | 5000 | 0 | 0 |
| 2e-4 | IG_matched | 5000 | 0 | 0 |
| 8e-4 | uniform_shrink | 4998 | 2 | 0 |
| 8e-4 | IG_matched | 4999 | 1 | 0 |

The three failed image-condition cases are retained rather than removed:

- `6353.pgm`, epsilon 8e-4, uniform_shrink: 3419 bit errors;
- `6606.pgm`, epsilon 8e-4, uniform_shrink: 4735 bit errors;
- `9002.pgm`, epsilon 8e-4, IG_matched: 4725 bit errors.

All four conditions satisfy the preregistered >=99% coding-success criterion, and every encoding classified as successful has exact message recovery.

## Historical-equivalence check

The six original raw blocks covering indices 0–1500 (6000 image-condition records) were compared record-by-record against the clean rerun using the key `(image, epsilon, method)`.

After excluding only `elapsed_s`, which is not a scientific outcome, the comparison found:

- 6000 / 6000 records scientifically identical;
- zero field discrepancies.

Across the full 5000-image rerun, the success/failure counts, identities of all three failed cases, message-bit totals, bit-error totals, change fractions, and PSNR summaries reproduce the previously stored aggregate V8 summary. Mean distortion values differ only at floating summation/compiler roundoff scale (approximately 1e-5 to 5e-5 absolute).

This provides a direct bridge between the traceable historical prefix and the complete clean rerun without claiming recovery of the missing historical binary.

## Provenance decision

**V8 actual-message STC realization and raw-provenance closure: PASS.**

The raw files are stored in `research_v8/results/V8_STC_RERUN/`, together with a machine-checkable SHA-256 manifest and aggregate summaries.

This decision closes the coding/runtime/raw-lineage portion of the V8 evidence chain. It does **not** make detector-facing claim C6 pass. C6 remains OPEN until the preregistered strong steganalysis tier is executed and its raw evidence, uncertainty analysis, and matched-payload comparisons are persisted.
