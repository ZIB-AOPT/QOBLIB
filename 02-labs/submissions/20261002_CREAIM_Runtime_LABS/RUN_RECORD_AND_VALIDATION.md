# Retained run record and validation supplement

This supplement explains the existing submission; it reports no new optimization runs. Source records are the unchanged instance summary CSVs and the public [run reference](https://github.com/hsm6954-boop/CREAIM-Runtime-QOBLIB-Reproducibility/blob/dfe167330fefd9b3158453deb9402c0cc0c433a8/RUNS.md). The public reference identifies the proprietary solver but does not redistribute its source or executable.

## Recorded execution information

- Solver build: `CREAIM-RUNTIME-LABS-20261002`. Its original SHA-256 remains in the summary CSVs and public reference.
- Classical, stochastic execution; 5 outer runs per instance; all 5 feasible and all 5 at the submitted best.
- Fixed outer seeds: `28123, 128126, 228129, 328132, 428135`.
- Recorded environment: Base44 sandbox; 4 vCPU x86_64; virtualized AuthenticAMD; Linux/gVisor; GCC 12.2.0; `OMP_NUM_THREADS=4`; no GPU or QPU. This describes the original runs, not the maintenance environment.
- The recorded protocol independently recomputes the full-sequence LABS energy before output.

| Instance | Submitted energy | Runs at submitted best | Recorded mean wall time (s) |
| --- | ---: | ---: | ---: |
| labs067 | 241 | 5/5 | 19.010000 |
| labs099 | 577 | 5/5 | 59.506000 |

The mean wall times above are those already published in RUNS.md and the unchanged Total Runtime fields. They do not establish first-hit time, per-run durations, or TTS.

## Information not recorded / N/A

- Time to Solution (TTS): **not recorded / N/A**. The retained records do not provide per-run first-hit timestamps. Mean wall time and success counts cannot reconstruct TTS.
- Objective time series: **not recorded / N/A**. No time-series artifact is retained or supplied; no synthetic series is created.
- Number, type, and range of non-zero coefficients in the proprietary reduced encoding: **not recorded / N/A** in the retained public evidence. The submitted decision-variable counts do not determine these quantities. A coefficient count from a different public LABS formulation would not describe this encoding and is not substituted.
- CPU runtime and individual run durations: **not recorded / N/A** beyond the published mean wall times.
- No additional benchmark runs or instances are claimed. The request for additional runs and broader problem-class coverage remains open; the proprietary solver and new run records are not available in these public checkouts.

## Artifact preservation and validation scope

The original solution files, summary CSVs, solver digests, solution digests, official-checker source digest, and frozen validation provenance are unchanged. The frozen validation baseline remains QOBLIB `4c0d8ba5965a286526e8bd49217007c1708c635f`; current maintenance checks are a separate observation, not a replacement of that provenance. The original official-checker source SHA-256 in Remarks identifies that historical evidence and is not redefined as the current source hash.

Upstream main at `55384509a610f040bea517a6c16079ce5c4edf0d` was synchronized with an ordinary merge preserving the PR's original history. No rebase or forced update was used.

The authoritative `qoblib-check-submission` was run with solution checking enabled and passed **2/2 instances**, matching the recorded baseline. Direct official LABS checks confirm energies **241 and 577**. The PR best-known-value comparison, Python CI tests, and static-site build are exercised locally; remote GitHub Actions status must be checked separately for the pushed commit. No Pages deployment is requested.

| Solution file | Preserved SHA-256 |
| --- | --- |
| `labs067_solution.sol` | `0b005ddac03cd11ac32cc4c656b27e8bf54b3a626841d2f430325a07cd7a8086` |
| `labs099_solution.sol` | `9d586695c0c97cbdd5a85f670fc9c65c15330d306c2ce2db58df424f5fa883c6` |

These checks validate the submitted sequences and artifact integrity; they neither rerun the proprietary optimizer nor prove optimality. Missing measurements, coefficient information, and additional-run requests remain for maintainer review.
