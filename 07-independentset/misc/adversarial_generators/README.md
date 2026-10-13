# Adversarial Maximum Independent Set generators

This directory contains the source and recorded parameters for ten generated
MIS instances.  All graph files use 1-based DIMACS vertices, as does each
reference solution.

## Instance families

| Instance | n | Edges | Exact alpha | Origin and evidence |
| :-- | --: | --: | --: | :-- |
| `aheg_n99_s31` | 99 | 2,780 | 7 | solver-guided evolutionary search; CPLEX later enumerated 56 optima |
| `hybrid_csp_spinglass_n180_s42` | 180 | 5,277 | 15 | hybrid CSP and frustrated spin-glass search; CPLEX later enumerated 11 optima |
| `frozen_xorsat_c3k3_compact_n700` | 700 | 5,226 | 175 | compact frozen (3,3)-XORSAT reduction |
| `frozen_xorsat_c3k3_compact_n800` | 800 | 5,996 | 200 | compact frozen (3,3)-XORSAT reduction |
| `frozen_xorsat_c3k3_compact_n1000` | 1,000 | 7,472 | 250 | compact frozen (3,3)-XORSAT reduction |
| `frozen_xorsat_c3k3_compact_n1200` | 1,200 | 8,988 | 300 | compact frozen (3,3)-XORSAT reduction |
| `frozen_xorsat_c3k3_regular_n1500` | 1,500 | 4,750 | 500 | regular frozen (3,3)-XORSAT reduction |
| `frozen_xorsat_v2_qc_l75_s1` | 900 | 6,750 | 225 | v2 quasi-cyclic frozen-XORSAT, lift 75, seed 1 |
| `frozen_xorsat_v2_qc_l100_s4` | 1,200 | 9,000 | 300 | v2 quasi-cyclic frozen-XORSAT, lift 100, seed 4 |
| `frozen_xorsat_v2_qc_l125_s1` | 1,500 | 11,250 | 375 | v2 quasi-cyclic frozen-XORSAT, lift 125, seed 1 |

The n=99 and n=180 graphs are small, dense, quantum-scale structural cases;
they are not presented as classically intractable.  The n=99 graph was solved
in about 1.2 seconds and the n=180 graph in about 53 seconds in the recorded
CPLEX validation.  Their value is to have more instances at the dense end of
the benchmark where quantum algorithms struggle due to high connectivity at
a scale that is quantum tractable.

The larger instances propose a new family of very sparse structurally difficult
instances in the range of 700-1500 nodes.
The n=700 compact graph is solver-dependent: recorded ReduMIS and mmwis
campaigns missed the exact optimum, while CPLEX subsequently proved
`alpha=175` in about 1,753 seconds.  The n=800 through n=1200 graphs are scaling
points from the same exactly certified family; no stronger claim is made here
without a matching current solver run.  For n=1500, recorded one-hour campaigns
found at most 497 with ReduMIS, 490 with mmwis, 489 with mmwiss, and 485 with
CPLEX, against the exact value 500.

The v2 family is a quasi-cyclic lift of the K3,3 Tanner protograph followed by
the compact four-vertices-per-clause encoding.  It keeps the exact clique-cover
certificate while imposing a more structured, girth-12 incidence pattern.  In
the source search workspace these three artifacts were named `hard_L75_s1`,
`hard_L100_s4`, and `hard_L125_s1`, respectively.  In
recorded one-hour, two-thread CPLEX runs, the best final incumbents were 213 of
225, 285 of 300, and 361 of 375 for lift sizes 75, 100, and 125.  Separate
ReduMIS screens found 222, 297, and 370.

## Exact XORSAT regeneration and verification

All eight XORSAT instances can be regenerated with the scripts provided.
The original compact and regular cases use seed 1.
The v2 quasi-cyclic cases use `(L, seed)` values
`(75, 1)`, `(100, 4)`, and `(125, 1)`.
The regeneration wrapper also adds QOBLIB's CC BY 4.0 data-license header as
DIMACS `c` comment lines:

```bash
python 07-independentset/misc/adversarial_generators/regenerate_xorsat.py
python 07-independentset/misc/adversarial_generators/regenerate_xorsat.py --check
python 07-independentset/misc/adversarial_generators/verify_selected.py
shasum -a 256 -c 07-independentset/misc/adversarial_generators/SHA256SUMS
```

For every compact or v2 instance, the consecutive groups of four vertices are
clause-assignment K4s.  They cover the graph, so an independent set contains at
most one vertex from each of the `n/4` blocks.  The planted solution contains
one compatible assignment from every block, proving `alpha=n/4`.

For the regular n=1500 instance, the first 500 vertices form 250 disjoint K2
variable blocks and the remaining vertices form 250 K4 clause blocks.  This
500-clique cover proves `alpha<=500`; the planted consistent assignment has
size 500, so equality holds.  `verify_selected.py` checks the graph headers,
solution feasibility, and every edge required by these clique-cover
certificates.

`SHA256SUMS` covers all ten graph and reference-solution files.  Solutions
are written as one-based nodelists, one vertex per line, matching QOBLIB's
reference-solution reader.

## Solver-guided small-instance generation

The exact n=99 AHEG parameters are stored in `aheg_n99_args.json`.  Equivalently:

```bash
python 07-independentset/misc/adversarial_generators/aheg_evolutionary.py \
  --n 99 --B_ex 1 --B_heu 1 --T 8 --M 8 --seed 31 \
  --p_low 0.48 --p_high 0.52 --c1_low 12 --c1_high 18 \
  --cert_budget 45 --heu_seeds 3 --mutations_per_parent 3 \
  --a1 15 --a2 8 --a3 3 --a4 6 --a5 6 --a6 5 --a7 3 --a8 2 \
  --b1 8 --b2 6 --b3 2 --lam 3 --mu 1.5 --xi 1.5 --zeta 3 \
  --w_ex 2 --w_heu 1
```

The n=180 search used:

```bash
python 07-independentset/misc/adversarial_generators/gpt_csp_spinglass.py \
  --mode full --density medium_graph_320 --seed 42 --pop 5 --gens 10 \
  --cplex_time 30 --heur_time 30 --heur_runs 1 \
  --output_prefix medium_dense_30s
```

Those two searches score candidates with external solver runs.  Their seeds and
source make the process reproducible, but wall-clock-sensitive candidate
ranking may not be byte-identical across CPLEX/ReduMIS versions and machines.
The committed graph files and SHA-256 manifest are therefore the canonical
artifacts.
