# Instances for Market Split

## Format Description

The market split problem can be expressed as finding a vector $x \in \{0,1\}^n$ such that $Ax = b$ for given $A \in \mathbb{N}^{m,n}$ and $b \in \mathbb{N}^m$.
We provide the instances in dat format, where the first line gives $m$ and $n$ and the consecutive $m$ lines contain $n + 1$ whitespace separated values: 
The first $n$ values are the entries of the repective row in $A$ and the last value is the respective entry in $b$.

This way, we can easily add or take away specific rows to increase or decrease the difficulty of the problem. 

## Instance Generation

All instances in this directory up to size $7$ were generated randomly with a script provided in [misc](./../misc/) using an instance generator written by Marc Pfetch.

Instances from size $8$ and up were generated using the script provided [here](./../misc/marketsplit_gen/).

The solutions that were used to generate the instances can be found [here](./instance_gen_set/).

## Adversarial planted instances (2026)

Ten additional instances cover `n=81` through `n=90`, `m=5` through `m=8`,
and coefficient caps from 1,000 through 100,000.  Their names retain the
existing `ms_<m>_<coefficient range>_<index>` prefix and append the generator
family and variable count.

| Instance | Variables | Constraints | Coefficient cap | Generator |
| :-- | --: | --: | --: | :-- |
| `ms_05_18000_128_ortho_n81` | 81 | 5 | 18,000 | tight-frame / spectral shaping |
| `ms_05_18000_191_ortho_n81` | 81 | 5 | 18,000 | tight-frame / spectral shaping |
| `ms_05_20000_053_ortho_n81` | 81 | 5 | 20,000 | tight-frame / spectral shaping |
| `ms_05_20000_228_ortho_n81` | 81 | 5 | 20,000 | tight-frame / spectral shaping |
| `ms_05_20000_453_v5_n81` | 81 | 5 | 20,000 | structural v5 |
| `ms_05_30000_058_v5_n84` | 84 | 5 | 30,000 | structural v5 |
| `ms_07_03000_098_v5_n86` | 86 | 7 | 3,000 | structural v5 |
| `ms_08_01000_019_v5_n88` | 88 | 8 | 1,000 | structural v5 |
| `ms_06_10000_068_v5_n90` | 90 | 6 | 10,000 | structural v5 |
| `ms_05_100000_043_v5_n90` | 90 | 5 | 100,000 | structural v5 |

The larger coefficients maintain a sparse feasible-solution regime while using
few constraints and therefore a high-dimensional integer kernel.  They are not
obtained by multiplying a smaller instance: each matrix is generated directly
within its stated coefficient range.  See
[the generator documentation](../misc/adversarial_generators/README.md) for the
construction rationale, exact seeds, bounded solver evidence, regeneration
commands, and the important limits of the hardness and uniqueness claims.

Reference planted solutions are in [`../solutions/`](../solutions/).
