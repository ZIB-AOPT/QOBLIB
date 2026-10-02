# CREAIM Runtime — QOBLIB 07-independentset submission

This submission reports **classical, stochastic, reference-blind** Maximum Independent Set (MIS) runs produced by CREAIM Runtime against public QOBLIB instances. It does **not** claim physical-QPU execution, quantum advantage, quantum speedup, universal solver superiority, or an independent proof of optimality.

## Submitted results

| Instance | CREAIM best | QOBLIB frozen reference | QOBLIB ledger status | Feasible runs | Runs at best |
| --- | ---: | ---: | --- | ---: | ---: |
| C125-9 | 34 | 34 | optimal | 10/10 | 10/10 |
| p_hat1500-3 | 94 | 94 | optimal | 10/10 | 9/10 |
| hamming10-4 | 40 | 40 | best known | 10/10 | 10/10 |

The CSV `Optimality Bound` field is deliberately `N/A` for every instance, including instances whose QOBLIB ledger is labeled `optimal`, because CREAIM does not provide an independent optimality proof.

## Workflow

1. Parse the public DIMACS MIS graph.
2. Build a degree-biased randomized greedy independent set.
3. Greedily fill to maximality.
4. Apply iterative local 1-to-2 exchange.
5. Apply randomized perturb/restart ILS.
6. Independently recheck stable-set feasibility.
7. Retain the best feasible solution from the fixed run protocol.

The solver does not read QOBLIB reference solutions, best-known values, or target objective values during search.

## Repetition protocol

- Algorithm type: Stochastic
- Paradigm: Classical
- Independent outer runs per instance: 10
- Seed base: `28123`
- Seed stride: `100003`
- Seeds: `28123, 128126, 228129, 328132, 428135, 528138, 628141, 728144, 828147, 928150`
- OpenMP threads: `OMP_NUM_THREADS=4`
- C125-9: 64 internal restarts × 500 ILS cycles per outer run
- p_hat1500-3: 128 internal restarts × 1000 ILS cycles per outer run
- hamming10-4: 128 internal restarts × 1000 ILS cycles per outer run
- Success threshold ε: `0` relative to the best value found by the submitted algorithm, as defined by the QOBLIB submission schema

## Hardware and software

- Execution environment: Base44 cloud sandbox
- CPU allocation: 4 vCPU
- Architecture: x86_64
- Reported CPU vendor/family/model: AuthenticAMD, family 25, model 17 (virtualized environment)
- OS/kernel boundary: Linux / gVisor sandbox
- Compiler: GCC / g++ 12.2.0
- Python: 3.11.16 for submission/evidence tooling
- GPU: none used
- QPU: none used

Mean end-to-end wall times for the fixed 10-run protocol:

- C125-9: `0.067599 s`
- p_hat1500-3: `0.977763 s`
- hamming10-4: `0.787105 s`

These timings are execution-environment observations only. No hardware-speed comparison or speedup claim is made.

## Source and solution integrity

- CREAIM MIS solver source SHA-256: `85bd754b14aa1679df290d2b5c68658ddfe225d1cb5209d85247c76bf027b76a`
- C125-9 solution SHA-256: `64f92597233cccbb0753406aa02f4baf32f8565b54fab738d46a469d4a30e15c`
- p_hat1500-3 solution SHA-256: `3d1183137106fc08c374aa78248f27d443ec995e5339aa9321d0a2a7e6d6ed20`
- hamming10-4 solution SHA-256: `25ab4f5354550dfb0826e0e13c94ce75165dc75b9a6e54cec777d1694784e81f`

## QOBLIB validation provenance

Submission preparation and local official validation were frozen against QOBLIB repository HEAD:

`4c0d8ba5965a286526e8bd49217007c1708c635f`

- QOBLIB `check_stableset` source SHA-256: `da4c3f2857abe9660455ab5d378f4d440c1a57b063480f395508750fe0d35ddb`
- QOBLIB `check_submission.py` source SHA-256: `0280b50a3ccd0f7855f41e1e1958bff53d42c96701064dd234c3cd55d4fd2f0f`
- Official `check_stableset` local execution: **3/3 VALID, exit code 0**
- QOBLIB higher-level submission validator with official checker enabled: **3/3 passed, Overall OK, exit code 0**

The GitHub-hosted QOBLIB CI result is separate from this local official-checker replay and will be determined by the Pull Request workflow.

## Claim boundary

Allowed interpretation: CREAIM Runtime produced valid classical MIS solutions that match the QOBLIB repository's listed objective values for the three submitted instances under the frozen provenance above.

Not claimed: physical quantum execution, quantum advantage, quantum speedup, a new public best, independent proof of optimality, or universal solver superiority.
