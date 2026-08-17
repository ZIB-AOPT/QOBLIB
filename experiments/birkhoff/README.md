# Dense minimum Birkhoff-decomposition experiments

This directory contains a reproducible exact-decomposition benchmark for the
fifteen dense Birkhoff instances that currently have no recorded solution:
`B64_4096_1` through `B64_4096_10`, and `B100_10000_1` through
`B100_10000_5`.

The solver keeps the residual matrix and coefficients as integers.  In each
iteration it finds a perfect matching in the positive residual support and
subtracts the smallest residual on that matching.  Consequently, every emitted
decomposition reconstructs the input matrix exactly and its coefficients sum
to the instance scale.

## Reproduce

Install Python with NumPy and SciPy, then run:

```bash
python experiments/birkhoff/benchmark_birkhoff.py \
  03-birkhoff/instances/qbench_64_dense.json /tmp/qbench_64_solution.json \
  --policy max_min_zero_low_sum
python experiments/birkhoff/benchmark_birkhoff.py \
  03-birkhoff/instances/qbench_100_dense.json /tmp/qbench_100_solution.json \
  --policy max_min_zero_low_sum
```

`max_min_zero_low_sum` first maximizes the smallest selected residual, then
maximizes the number of entries made zero by the subtraction, and finally
minimizes the matching's residual sum.  The latter two rules are tie-breakers
within the same max-min threshold.

## Measured ablation

All figures below are exact term counts; lower is better.  Each policy was run
once over every instance on the same input files.

| Matching policy | Mean terms, 64x64 | Mean terms, 100x100 |
| --- | ---: | ---: |
| Maximum total residual weight | 383.1 | 679.6 |
| Max-min threshold | 280.4 | 473.8 |
| Max-min + maximize eliminated threshold entries | 261.1 | 437.6 |
| Max-min + minimize residual sum | 265.2 | 438.2 |
| **Max-min + both tie-breakers** | **254.7** | **423.4** |

The final policy found 256, 252, 254, 250, 259, 252, 255, 259, 254, and 256
terms respectively for `B64_4096_1` through `B64_4096_10`; it found 420, 424,
424, 425, and 424 terms for `B100_10000_1` through `B100_10000_5`.

## Method context

The max-min component is a standard Birkhoff-style strategy: it selects a
support-perfect matching whose minimum residual is as large as possible.
The focused tie-breakers were chosen empirically for these QOBLIB dense inputs.
For background, see Valls et al., *Birkhoff's Decomposition Revisited* (IEEE/
ACM Transactions on Networking, 2021, DOI
[10.1109/TNET.2021.3088327](https://doi.org/10.1109/TNET.2021.3088327)) and
Daskin, *Lowering LCU Circuit Width through Maximum-Weight Birkhoff-von
Neumann Decomposition* ([arXiv:2605.27430](https://arxiv.org/abs/2605.27430)).
