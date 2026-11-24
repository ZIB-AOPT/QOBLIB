# MIS-QAOA independent-set hardware results

This pull request contributes quantum-hardware results for 22 QOBLIB maximum independent set instances, using QAOA at depth $p=2$ on IBM Quantum's `ibm_boston` backend.

## Contributions

The main contributions of this submission are:

- We present a more efficient end-to-end pipeline that matches or improves optimality gaps for hardware experiments while reducing reported total runtime compared to previous submissions by JIJ (same `ibm_boston` backend) and Aqarios.
- We design a custom warm start policy over the clique cover encoding of the optimization problem.
- We exploit the clique encoding to rewrite residual penalties and reduce the number of  logical two-qubit gates of the cost layer.
- We develop a post-processing pipeline that uses measured marginal distributions to repair invalid clique registers, followed by classical polishing and reconstruction on the original graph.
- We evaluate the end-to-end workflow on quantum hardware for 22 QOBLIB instances, obtaining solutions that match the reference optimum after postprocessing.

## Method

The workflow combines exact graph reductions, clique-cover based QAOA with warm start and fixed angles, and classical postprocessing.

1. **Preprocessing:** Apply exact graph reductions and partition the reduced graph into disjoint cliques. Select the reduced graph requiring fewer encoded qubits and retain the information needed to reconstruct solutions on the original graph.

   For the reduced graph $G_{\mathrm{red}}=(V_{\mathrm{red}},E_{\mathrm{red}})$, write $V_{\mathrm{red}}=\bigsqcup_{i=1}^{k}C_i$, with $C_i=(v_{i1},\ldots,v_{im_i})$. Each clique has a categorical variable $t_i\in\{0,1,\ldots,m_i\}$: $t_i=0$ selects no vertex, while $t_i=j>0$ selects $v_{ij}$. An assignment $t=(t_1,\ldots,t_k)$ therefore selects at most one vertex per clique. Letting $x_v(t)$ indicate whether vertex $v$ is selected, and $E_R$ contain the residual inter-clique edges, the penalized MIS objective is then given by

   $$
   F(t)=\sum_{v\in V_{\mathrm{red}}}x_v(t) -\lambda_E\sum_{(u,v)\in E_R}x_u(t)x_v(t), \qquad \lambda_E=1.1.
   $$

2. **QAOA sampling:** Prepare a mean-field warm start and use a Hamming-weight preserving mixer for the clique encoding, allowing at most one selected vertex per clique. Penalize residual inter-clique edges in the cost Hamiltonian. Choose equivalent reformulations as needed to reduce logical RZZ count, then compile with SABRE at optimization level 3, with fractional gates disabled. Sample the circuit using fixed ramp angles.

3. **Postprocessing:** Repair invalid clique registers using probabilities estimated from the measured samples. Greedily remove remaining vertex conflicts and add compatible vertices by minimum degree until the set is maximal. Keep the best set from each run, lift it back to the original graph through the exact reductions, and validate its independence and cardinality.

Each instance is evaluated over five independent hardware runs with the same QAOA circuit, angles, and shot count. Runs use 4,096, 10,000, or 25,000 shots, selected according to the dimension of the clique-feasible subspace and the size of the compiled circuit for that instance. The complete workflow reaches the reference optimum in all runs for each of the 22 instances. Summary CSVs and .sol files for the different instances report the final results after post-processing.

## Results

### Instance summary

The full pipeline finds a feasible independent set matching the expected maximum independent set size for 22 QOBLIB instances that fit on hardware after reduction. The table reports graph dimensions before and after reductions, encoded qubits (including null ancillas), QAOA depth $p=2$, shots per run, and mean runtimes in seconds. Circuit and angles are identical across runs for each instance. Total runtime is CPU runtime plus `circuit_execution_runtime`, and equals time to solution for this submission.

| Instance | Original (n, m) | Kernel (n, m) | Qubits | QAOA depth p | Shots/run | Reference MIS | Best MIS | Gap (%) | CPU (s) | QPU (`circuit_execution_runtime`, s) | Total (s) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| [`farm`](farm/) | (17, 39) | (12, 14) | 14 | 2 | 4,096 | 10 | 10 | 0.00 | 0.10 | 1.12 | 1.22 |
| [`johnson8-2-4`](johnson8-2-4/) | (28, 210) | (28, 210) | 35 | 2 | 4,096 | 7 | 7 | 0.00 | 0.43 | 1.41 | 1.84 |
| [`ibm32`](ibm32/) | (32, 90) | (21, 24) | 29 | 2 | 4,096 | 13 | 13 | 0.00 | 0.20 | 1.12 | 1.32 |
| [`karate`](karate/) | (34, 78) | (22, 4) | 24 | 2 | 4,096 | 20 | 20 | 0.00 | 0.09 | 1.08 | 1.17 |
| [`football`](football/) | (35, 118) | (23, 18) | 30 | 2 | 4,096 | 16 | 16 | 0.00 | 0.16 | 1.11 | 1.27 |
| [`chesapeake`](chesapeake/) | (39, 170) | (21, 16) | 25 | 2 | 4,096 | 17 | 17 | 0.00 | 0.18 | 1.12 | 1.30 |
| [`MANN-a9`](MANN-a9/) | (45, 918) | (45, 918) | 48 | 2 | 4,096 | 3 | 3 | 0.00 | 0.52 | 1.46 | 1.98 |
| [`insecta-ant-colony1-day38`](insecta-ant-colony1-day38/) | (56, 1,134) | (25, 171) | 30 | 2 | 4,096 | 6 | 6 | 0.00 | 0.30 | 1.32 | 1.62 |
| [`hamming6-2`](hamming6-2/) | (64, 1,824) | (64, 1,824) | 66 | 2 | 4,096 | 2 | 2 | 0.00 | 0.75 | 1.84 | 2.59 |
| [`hamming6-4`](hamming6-4/) | (64, 704) | (64, 704) | 80 | 2 | 25,000 | 12 | 12 | 0.00 | 4.24 | 12.42 | 16.65 |
| [`sloane_1dc_64`](sloane_1dc_64/) | (64, 543) | (46, 317) | 56 | 2 | 25,000 | 10 | 10 | 0.00 | 2.93 | 9.74 | 12.67 |
| [`johnson8-4-4`](johnson8-4-4/) | (70, 1,855) | (70, 1,855) | 76 | 2 | 25,000 | 5 | 5 | 0.00 | 3.67 | 12.50 | 16.16 |
| [`es60fst03`](es60fst03/) | (113, 142) | (8, 13) | 11 | 2 | 4,096 | 55 | 55 | 0.00 | 0.14 | 1.11 | 1.24 |
| [`johnson16-2-4`](johnson16-2-4/) | (120, 5,460) | (120, 5,460) | 135 | 2 | 25,000 | 15 | 15 | 0.00 | 9.29 | 17.84 | 27.14 |
| [`es60fst01`](es60fst01/) | (123, 159) | (72, 28) | 83 | 2 | 4,096 | 60 | 60 | 0.00 | 1.21 | 1.11 | 2.32 |
| [`sloane_1dc_128`](sloane_1dc_128/) | (128, 1,471) | (106, 1,123) | 124 | 2 | 25,000 | 16 | 16 | 0.00 | 6.18 | 16.41 | 22.60 |
| [`sloane_1zc_128`](sloane_1zc_128/) | (128, 1,120) | (112, 980) | 137 | 2 | 25,000 | 18 | 18 | 0.00 | 6.95 | 15.26 | 22.22 |
| [`sloane_2dc_128`](sloane_2dc_128/) | (128, 5,173) | (70, 1,949) | 74 | 2 | 4,096 | 5 | 5 | 0.00 | 1.09 | 2.22 | 3.31 |
| [`insecta-ant-colony3-day09`](insecta-ant-colony3-day09/) | (160, 8,883) | (116, 4,442) | 126 | 2 | 25,000 | 9 | 9 | 0.00 | 7.44 | 20.55 | 27.99 |
| [`es60fst04`](es60fst04/) | (162, 238) | (59, 98) | 86 | 2 | 25,000 | 78 | 78 | 0.00 | 5.61 | 7.20 | 12.81 |
| [`es60fst02`](es60fst02/) | (186, 280) | (27, 46) | 40 | 2 | 10,000 | 88 | 88 | 0.00 | 0.85 | 2.84 | 3.69 |
| [`c-fat200-1`](c-fat200-1/) | (200, 1,534) | (37, 37) | 55 | 2 | 10,000 | 18 | 18 | 0.00 | 0.92 | 2.73 | 3.65 |

## Runtime

Runtimes are averaged over five runs, in seconds. `CPU Runtime` includes preprocessing, warm-start preparation, angle acquisition, circuit construction, shot selection, postprocessing, reconstruction, and scoring bitstrings. `circuit_execution_runtime` is the measured circuit execution time, from Qiskit's `circuits_execution_time_ns` converted to seconds, and reported as `QPU Runtime`. Billed runtime usage is separately recorded in each instance's summary under `Remarks`. `Total Runtime = CPU Runtime + circuit_execution_runtime`; `Time to Solution` is the total runtime including sampling and classical processing. Compilation and queue time are excluded, following [CONTRIBUTING.md](../../../CONTRIBUTING.md).

Classical processing ran on a MacBook Pro (`MacBookPro18,2`) with an Apple M1 Max, 10 CPU cores, 64 GB RAM, and macOS 26.6.2. `ibm_boston` was used as the quantum backend.

## Comparison against baselines

We compare against submissions from [JIJ (2026-07-09)](../20260709_JIJ/) and [Aqarios (2026-07-11)](../20260711_Aqarios_Optimizer/). JIJ uses `ibm_boston` with an Apple M4 / 16 GB CPU host and ten runs per instance; Aqarios uses `ibm_fez` with a MacBook Pro M5 and five runs per instance. This submission uses `ibm_boston` with an Apple M1 Max / 64 GB CPU host and five runs per instance.

`Best / gap` gives the best feasible MIS size and the corresponding percentage gap to the same reference solution. Total runtime columns report mean total runtimes per run, taken from each submission; Aqarios separately also reports a `Time to Solution` field. Runtimes (seconds) and optimality gaps are rounded to two decimal places. A dash means no submitted result for that instance.

| Instance | Ours best / gap (%) | Ours total (s) | JIJ best / gap (%) | JIJ total (s) | Aqarios best / gap (%) | Aqarios total (s) | Aqarios time to solution (s) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `farm` | 10 / 0.00 | 1.22 | [10 / 0.00](../20260709_JIJ/farm/farm_summary.csv) | 3.41 | — | — | — |
| `johnson8-2-4` | 7 / 0.00 | 1.84 | [3 / 57.14](../20260709_JIJ/johnson8-2-4/johnson8-2-4_summary.csv) | 16.28 | — | — | — |
| `ibm32` | 13 / 0.00 | 1.32 | [13 / 0.00](../20260709_JIJ/ibm32/ibm32_summary.csv) | 9.57 | — | — | — |
| `karate` | 20 / 0.00 | 1.17 | [20 / 0.00](../20260709_JIJ/karate/karate_summary.csv) | 3.15 | — | — | — |
| `football` | 16 / 0.00 | 1.27 | [16 / 0.00](../20260709_JIJ/football/football_summary.csv) | 4.91 | — | — | — |
| `chesapeake` | 17 / 0.00 | 1.30 | [17 / 0.00](../20260709_JIJ/chesapeake/chesapeake_summary.csv) | 14.30 | — | — | — |
| `MANN-a9` | 3 / 0.00 | 1.98 | [3 / 0.00](../20260709_JIJ/MANN-a9/MANN-a9_summary.csv) | 68.09 | — | — | — |
| `insecta-ant-colony1-day38` | 6 / 0.00 | 1.62 | [6 / 0.00](../20260709_JIJ/insecta-ant-colony1-day38/insecta-ant-colony1-day38_summary.csv) | 37.74 | — | — | — |
| `hamming6-2` | 2 / 0.00 | 2.59 | [2 / 0.00](../20260709_JIJ/hamming6-2/hamming6-2_summary.csv) | 132.98 | — | — | — |
| `hamming6-4` | 12 / 0.00 | 16.65 | [12 / 0.00](../20260709_JIJ/hamming6-4/hamming6-4_summary.csv) | 57.31 | — | — | — |
| `sloane_1dc_64` | 10 / 0.00 | 12.67 | [10 / 0.00](../20260709_JIJ/sloane_1dc_64/sloane_1dc_64_summary.csv) | 32.74 | — | — | — |
| `johnson8-4-4` | 5 / 0.00 | 16.16 | [5 / 0.00](../20260709_JIJ/johnson8-4-4/johnson8-4-4_summary.csv) | 145.67 | — | — | — |
| `es60fst03` | 55 / 0.00 | 1.24 | [55 / 0.00](../20260709_JIJ/es60fst03/es60fst03_summary.csv) | 26.93 | — | — | — |
| `johnson16-2-4` | 15 / 0.00 | 27.14 | [15 / 0.00](../20260709_JIJ/johnson16-2-4/johnson16-2-4_summary.csv) | 414.75 | — | — | — |
| `es60fst01` | 60 / 0.00 | 2.32 | [60 / 0.00](../20260709_JIJ/es60fst01/es60fst01_summary.csv) | 7.87 | — | — | — |
| `sloane_1dc_128` | 16 / 0.00 | 22.60 | [14 / 12.50](../20260709_JIJ/sloane_1dc_128/sloane_1dc_128_summary.csv) | 94.65 | [16 / 0.00](../20260711_Aqarios_Optimizer/sloane_1dc_128/sloane_1dc_128_summary.csv) | 315.74 | 39.06 |
| `sloane_1zc_128` | 18 / 0.00 | 22.22 | [16 / 11.11](../20260709_JIJ/sloane_1zc_128/sloane_1zc_128_summary.csv) | 89.39 | [18 / 0.00](../20260711_Aqarios_Optimizer/sloane_1zc_128/sloane_1zc_128_summary.csv) | 312.27 | 52.87 |
| `sloane_2dc_128` | 5 / 0.00 | 3.31 | [5 / 0.00](../20260709_JIJ/sloane_2dc_128/sloane_2dc_128_summary.csv) | 6.85 | [5 / 0.00](../20260711_Aqarios_Optimizer/sloane_2dc_128/sloane_2dc_128_summary.csv) | 290.43 | 42.27 |
| `insecta-ant-colony3-day09` | 9 / 0.00 | 27.99 | [8 / 11.11](../20260709_JIJ/insecta-ant-colony3-day09/insecta-ant-colony3-day09_summary.csv) | 388.20 | — | — | — |
| `es60fst04` | 78 / 0.00 | 12.81 | [76 / 2.56](../20260709_JIJ/es60fst04/es60fst04_summary.csv) | 27.02 | [78 / 0.00](../20260711_Aqarios_Optimizer/es60fst04/es60fst04_summary.csv) | 230.15 | 121.94 |
| `es60fst02` | 88 / 0.00 | 3.69 | [86 / 2.27](../20260709_JIJ/es60fst02/es60fst02_summary.csv) | 51.00 | [88 / 0.00](../20260711_Aqarios_Optimizer/es60fst02/es60fst02_summary.csv) | 240.09 | 131.14 |
| `c-fat200-1` | 18 / 0.00 | 3.65 | [18 / 0.00](../20260709_JIJ/c-fat200-1/c-fat200-1_summary.csv) | 7.49 | — | — | — |

Across the 22 shared instances, this submission matches JIJ's best MIS size on 16 and improves it on six. Across the five instances shared with Aqarios, it matches all five best solutions. Note that the submissions can use different CPUs, quantum backends and shot budgets.

## Metadata

A paper is currently in preparation, hence the `reference` field is set to `N/A`, and specific details on the implementation of the end-to-end pipeline have been limited accordingly. Reference will be provided once available. This method does not certify optimality, hence optimality bound is reported as `N/A`.

## AI disclosure

**assisted** — OpenAI Codex (GPT-6 Sol) assisted with drafting and revising portions of this README and submission CSVs. Solver code drafted with OpenAI Codex (GPT-6 Astra), then reviewed and edited.
