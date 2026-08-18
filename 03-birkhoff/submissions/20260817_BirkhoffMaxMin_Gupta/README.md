# Exact Birkhoff decompositions, max-min matching

Deterministic exact decompositions for all 375 benchmark instances.

The solver repeatedly picks a positive perfect matching with the largest
possible minimum residual, breaking ties by first maximising the number of
residual entries it zeroes out and then minimising the matching residual sum.
All arithmetic is on the scaled integers, so every decomposition reconstructs
its matrix exactly and passes `03-birkhoff/check` at the default tolerance of 0.

Fifteen instances, the `B64_4096_*` and `B100_10000_*` families, had no feasible
solution on record when these were produced.

The objective is the number of permutation matrices. No optimality is claimed.

Each objective time series records `Time`, `Incumbent` (the number of matrices
placed so far) and `Error` (the normalised squared Frobenius residual). The
incumbent grows as the decomposition is built, so the series is non-decreasing
rather than non-increasing; this is expected for a constructive method and is a
known limitation of the current validator.

## Coverage

| family | instances | matrices, best | matrices, worst |
| :--- | ---: | ---: | ---: |
| B100_10000 | 5 | 420 | 425 |
| B100_100 | 10 | 274 | 284 |
| B10_10 | 10 | 10 | 20 |
| B10_100 | 10 | 51 | 54 |
| B11_11 | 10 | 11 | 30 |
| B11_121 | 10 | 55 | 59 |
| B12_12 | 10 | 12 | 41 |
| B12_144 | 10 | 60 | 64 |
| B13_13 | 10 | 13 | 42 |
| B13_169 | 10 | 65 | 68 |
| B14_14 | 10 | 14 | 45 |
| B14_196 | 10 | 68 | 72 |
| B15_15 | 10 | 15 | 51 |
| B15_225 | 10 | 72 | 76 |
| B16_16 | 10 | 16 | 50 |
| B16_256 | 10 | 77 | 79 |
| B24_24 | 10 | 24 | 70 |
| B24_576 | 10 | 103 | 107 |
| B32_1024 | 10 | 156 | 160 |
| B32_32 | 10 | 67 | 101 |
| B3_3 | 10 | 2 | 3 |
| B3_9 | 10 | 4 | 5 |
| B48_2304 | 10 | 208 | 212 |
| B48_48 | 10 | 122 | 141 |
| B4_16 | 10 | 8 | 10 |
| B4_4 | 10 | 3 | 4 |
| B5_25 | 10 | 16 | 17 |
| B5_5 | 10 | 3 | 5 |
| B64_4096 | 10 | 250 | 259 |
| B64_64 | 10 | 163 | 173 |
| B6_36 | 10 | 24 | 26 |
| B6_6 | 10 | 6 | 7 |
| B7_49 | 10 | 29 | 33 |
| B7_7 | 10 | 7 | 8 |
| B8_64 | 10 | 34 | 37 |
| B8_8 | 10 | 8 | 8 |
| B9_81 | 10 | 39 | 41 |
| B9_9 | 10 | 9 | 22 |

Solver and reproduction notes: https://github.com/mnn31/qoblib-birkhoff
