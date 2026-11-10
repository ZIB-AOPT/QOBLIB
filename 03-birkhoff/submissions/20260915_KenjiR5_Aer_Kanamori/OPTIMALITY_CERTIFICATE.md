# Public instance-specific optimality certificates for the R5 Birkhoff submission

Scope: 21 fixed, public Birkhoff benchmark instances in QOBLIB PR #76. The certificates concern the submitted permutation-matrix decompositions, **not** the internals or general performance of the proprietary estimator.

## Exact mathematical argument

For an instance with scaled doubly stochastic matrix D, the objective is to minimize the number k of permutation matrices P_i in a convex combination D = sum_i w_i P_i, where w_i >= 0 and sum_i w_i = scale.

1. **Upper bound:** The submitted solution supplies k permutation vectors and nonnegative integer weights whose sum is `scale`; direct integer reconstruction exactly matches the public target matrix. Hence OPT <= k.
2. **Lower bound:** Enumerate every subset of t distinct permutation matrices for every 1 <= t < k, using all n! possible permutations (n = 3 or 4). Solve the corresponding exact linear system over rational numbers. No tested subset admits a nonnegative solution. A feasible decomposition with dependent support can always be reduced to a smaller independent support, so it suffices to check independent subsets. Hence OPT >= k.
3. **Conclusion:** The two bounds coincide: OPT = k for each listed instance.

Reproduction: from the repository checkout, run `python 03-birkhoff/submissions/20260915_KenjiR5_Aer_Kanamori/verify_optimality.py`. The verifier uses Python standard-library `fractions.Fraction` and reads only the public QOBLIB instance JSON and the submitted solution JSON files.

| Instance | Submitted objective | Proven lower bound | Proven optimum |
| --- | ---: | ---: | ---: |
| B3_3_1 | 2 | 2 | 2 |
| B3_3_2 | 3 | 3 | 3 |
| B3_3_3 | 3 | 3 | 3 |
| B3_3_4 | 3 | 3 | 3 |
| B3_3_5 | 3 | 3 | 3 |
| B3_3_6 | 3 | 3 | 3 |
| B3_3_7 | 2 | 2 | 2 |
| B3_3_8 | 3 | 3 | 3 |
| B3_3_9 | 2 | 2 | 2 |
| B3_3_10 | 3 | 3 | 3 |
| B3_9_1 | 5 | 5 | 5 |
| B3_9_2 | 5 | 5 | 5 |
| B3_9_3 | 5 | 5 | 5 |
| B3_9_4 | 5 | 5 | 5 |
| B3_9_5 | 4 | 4 | 4 |
| B3_9_6 | 5 | 5 | 5 |
| B3_9_7 | 4 | 4 | 4 |
| B3_9_8 | 4 | 4 | 4 |
| B3_9_9 | 4 | 4 | 4 |
| B3_9_10 | 4 | 4 | 4 |
| B4_4_5 | 4 | 4 | 4 |

**Caveats:** This is a proof of optimality of the *released solutions* for these particular public instances. It is not proof of optimality for unseen instances, independent confirmation of five estimator runs, a claim of new best-known values, or QOBLIB maintainer acceptance. No raw measurement records, internal acquisition settings, proprietary estimator algorithms, or other sensitive implementation details are published.

**Run-count preservation:** `B3_9_4` remains `# Runs = 5`, `# Feasible Runs = 4`, and `# Successful Runs = 4`; all other 20 instance records remain 5/5. The new certificates do not alter historical run outcomes.
