# Retained run record and validation supplement

This supplement explains the existing submission; it reports no new optimization runs. Source records are the unchanged instance summary CSVs and the public [run reference](https://github.com/hsm6954-boop/CREAIM-Runtime-QOBLIB-Reproducibility/blob/dfe167330fefd9b3158453deb9402c0cc0c433a8/RUNS.md). The public reference identifies the proprietary solver but does not redistribute its source or executable.

## Recorded execution information

- Solver build: `CREAIM-RUNTIME-MIS-20261002`. Its original SHA-256 remains in the summary CSVs and public reference.
- Classical, stochastic execution; 10 outer runs per instance; all 10 feasible.
- Fixed outer seeds: `28123, 128126, 228129, 328132, 428135, 528138, 628141, 728144, 828147, 928150` (base 28123, stride 100003).
- Recorded environment: Base44 sandbox; 4 vCPU x86_64; virtualized AuthenticAMD; Linux/gVisor; GCC 12.2.0; `OMP_NUM_THREADS=4`; no GPU or QPU. This describes the original runs, not the maintenance environment.

| Instance | Submitted objective | Runs at submitted best | Recorded mean wall time (s) |
| --- | ---: | ---: | ---: |
| C125-9 | 34 | 10/10 | 0.067599 |
| hamming10-4 | 40 | 10/10 | 0.787105 |
| p_hat1500-3 | 94 | 9/10 | 0.977763 |

The mean wall times above are those already published in RUNS.md and the unchanged Total Runtime fields. They do not establish first-hit time, per-run durations, or TTS.

## Information not recorded / N/A

- Time to Solution (TTS): **not recorded / N/A**. The retained records do not provide per-run first-hit timestamps. Mean wall time and success counts cannot reconstruct TTS.
- Objective time series: **not recorded / N/A**. No time-series artifact is retained or supplied; no synthetic series is created.
- CPU runtime and individual run durations: **not recorded / N/A** beyond the published mean wall times.
- No additional benchmark runs or instances are claimed. The request to evaluate more of the problem class remains open; the proprietary solver and new run records are not available in these public checkouts.

## Artifact preservation and validation scope

The original solution files, summary CSVs, solver digests, solution digests, and frozen validation provenance are unchanged. The frozen validation baseline remains QOBLIB `4c0d8ba5965a286526e8bd49217007c1708c635f`; current maintenance checks are a separate observation, not a replacement of that provenance.

Upstream main at `55384509a610f040bea517a6c16079ce5c4edf0d` was synchronized with an ordinary merge preserving the PR's original history. No rebase or forced update was used.

The authoritative `qoblib-check-submission` was run with solution checking enabled and passed **3/3 instances**, matching the recorded baseline. Direct official stable-set checks confirm sizes **34, 40, 94**. The PR best-known-value comparison passed. Python CI tests and the static-site build are also exercised locally; remote GitHub Actions status must be checked separately for the pushed commit. No Pages deployment is requested.

| Solution file | Preserved SHA-256 |
| --- | --- |
| `C125-9_solution.sol` | `64f92597233cccbb0753406aa02f4baf32f8565b54fab738d46a469d4a30e15c` |
| `hamming10-4_solution.sol` | `25ab4f5354550dfb0826e0e13c94ce75165dc75b9a6e54cec777d1694784e81f` |
| `p_hat1500-3_solution.sol` | `3d1183137106fc08c374aa78248f27d443ec995e5339aa9321d0a2a7e6d6ed20` |

These checks validate feasibility and artifact integrity; they neither rerun the proprietary optimizer nor prove optimality. Missing measurements and additional-instance requests remain for maintainer review.
