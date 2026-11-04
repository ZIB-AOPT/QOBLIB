# Adversarial Market Split generator

This directory contains the generators and exact parameters for the ten added
Market Split instances.  Run from the repository root with Python 3.9 or newer:

```bash
python -m venv /tmp/qoblib-ms-venv
/tmp/qoblib-ms-venv/bin/pip install -r 01-marketsplit/misc/adversarial_generators/requirements.txt
/tmp/qoblib-ms-venv/bin/python 01-marketsplit/misc/adversarial_generators/regenerate_selected.py
/tmp/qoblib-ms-venv/bin/python 01-marketsplit/misc/adversarial_generators/regenerate_selected.py --check
shasum -a 256 -c 01-marketsplit/misc/adversarial_generators/SHA256SUMS
```

The second command regenerates the `.dat` files and planted `.opt.sol` files;
the third independently regenerates them in a temporary directory and requires
byte-for-byte equality with the repository copies.  Every generated solution is
also checked for Booleanity, exact integer equality `A x = b`, and QOBLIB's
exact-midpoint invariant `2b = A1`.  `SHA256SUMS` covers all ten instance and
solution files.

## Selected instances and solver evidence

| Instance | Family | n | m | Coefficient cap | Outer seed | Recorded screening |
| :-- | :-- | --: | --: | --: | --: | :-- |
| `ms_05_18000_128_ortho_n81` | ortho | 81 | 5 | 18,000 | 128 | isolated 28-configuration race, no solution in 7,081 s |
| `ms_05_18000_191_ortho_n81` | ortho | 81 | 5 | 18,000 | 191 | isolated 28-configuration race, no solution in 7,082 s |
| `ms_05_20000_053_ortho_n81` | ortho | 81 | 5 | 20,000 | 53 | isolated 28-configuration race, no solution in 7,085 s |
| `ms_05_20000_228_ortho_n81` | ortho | 81 | 5 | 20,000 | 228 | isolated 28-configuration race, no solution in 7,083 s |
| `ms_05_20000_453_v5_n81` | v5 | 81 | 5 | 20,000 | 453 | isolated 28-configuration race, no solution in 7,084 s |
| `ms_05_30000_058_v5_n84` | v5 | 84 | 5 | 30,000 | 58 | batch 28-configuration screen, no solution recorded in 7,082 s |
| `ms_07_03000_098_v5_n86` | v5 | 86 | 7 | 3,000 | 98 | batch 28-configuration screen, no solution recorded in 7,083 s |
| `ms_08_01000_019_v5_n88` | v5 | 88 | 8 | 1,000 | 19 | batch 28-configuration screen, no solution recorded in 7,084 s |
| `ms_06_10000_068_v5_n90` | v5 | 90 | 6 | 10,000 | 68 | batch 28-configuration screen, no solution recorded in 7,080 s |
| `ms_05_100000_043_v5_n90` | v5 | 90 | 5 | 100,000 | 43 | batch 28-configuration screen, no solution recorded in 7,083 s |

The races used `solvediophant` configurations spanning BKZ/partial-BKZ,
block sizes 10 through 75, and limited-discrepancy search.  A bounded failure is
solver-specific evidence, not a proof of intrinsic hardness.  The five batch
results are screening results and were not used as feasibility evidence.

## Why the coefficients are large

The coefficient caps are deliberate rather than arbitrary scaling.  For a
balanced planted split, a local-limit estimate gives roughly

```text
log2(D_critical) = n/m - 0.5 log2(pi n / 6).
```

Using few constraints keeps the integer-kernel dimension `n-m` high, but it
also requires larger `D` to avoid an exponential number of unrelated feasible
splits.  The selected caps therefore range from 1,000 (m=8) to 100,000 (m=5).
The range is itself part of the benchmark: it tests coefficient sensitivity as
well as size.  The generators plant a balanced solution, retain exact integer
arithmetic, and use a randomized guard against unexpected alternatives.  The
guard is not a proof of uniqueness; exact-midpoint instances always retain the
complement solution.

The `ortho` family shapes the row spectrum toward a tight frame.  The v5 family
uses structured near-kernel directions and enforces an exact LP midpoint plus
row-magnitude uniformity.  No solver is called during generation.
