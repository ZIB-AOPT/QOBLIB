# CREAIM Runtime — QOBLIB LABS submission

This submission reports **classical, stochastic, reference-blind** Low Autocorrelation Binary Sequence (LABS) runs produced by CREAIM Runtime. It does **not** claim physical-QPU execution, quantum advantage, quantum speedup, universal solver superiority, a new public best, or an independent proof of optimality.

## Submitted results

| Instance | CREAIM best energy | QOBLIB frozen reference | QOBLIB ledger status | Feasible runs | Runs at best |
| --- | ---: | ---: | --- | ---: | ---: |
| `labs067` | **241** | 241 | best known | 5/5 | 5/5 |
| `labs099` | **577** | 577 | best known | 5/5 | 5/5 |

## Protocol

- Solver: CREAIM LABS Skew-Symmetric Self-Avoiding Search V3
- Solver source SHA-256: `f1a931f89d6abb64721d4fc4edf21500cd4cbcd0f5391c46977eb6dd2a897a19`
- Algorithm type: Stochastic
- Paradigm: Classical
- Search is reference-blind: the solver source contains no QOBLIB target energies or reference solutions.
- Fixed outer seeds: `28123, 128126, 228129, 328132, 428135`
- Fixed per-run budget: 8,000 self-avoiding segments; walk factor 8
- `OMP_NUM_THREADS=4`
- Every candidate is scored using the exact LABS autocorrelation energy.
- Emitted solutions are independently re-evaluated before write-out.

## Official validation

Frozen QOBLIB source commit: `4c0d8ba5965a286526e8bd49217007c1708c635f`

- `check_labs` source SHA-256: `521a89ea4ae02e98461b053ec614d024899365631fe02c3b73b3b45e71c8beb9`
- `labs067`: official checker exit 0 / `VALID`, energy 241
- `labs099`: official checker exit 0 / `VALID`, energy 577

The official LABS checker states that results for `k >= 67` are not known internally; therefore checker `VALID` establishes sequence validity and recomputed energy, while the `best known` classification comes separately from QOBLIB's published `02-labs/solutions/README.md` ledger.

## Claim boundary

- No proven optimum claim for n=67 or n=99.
- No new best-known claim: both values match QOBLIB's frozen published best-known energies.
- No physical QPU execution.
- No quantum advantage or quantum speedup claim.
- No general solver-superiority claim.
