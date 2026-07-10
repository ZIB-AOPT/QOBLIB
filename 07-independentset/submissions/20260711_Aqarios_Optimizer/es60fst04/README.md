# Submission for es60fst04
This directory contains the submission for the problem **es60fst04**
| Field | Value 1 |
| --- | --- |
| Problem | `es60fst04` |
| Submitter | David Bucher |
| Affiliation | Aqarios GmbH |
| Date | 2026-07-11 00:36:43 |
| ====== |  |
| Reference | Paper: https://arxiv.org/pdf/2604.02083. In the process of becoming a Qiskit Function |
| Best Objective Value | 78 |
| Optimality Bound | N/A |
| ====== |  |
| Modeling Approach | Binary Linear Program |
| # Decision Variables | 162 |
| # Binary Variables | 162 |
| # Integer Variables | N/A |
| # Continuous Variables | N/A |
| # Non-Zero Coefficients | 638 |
| Coefficients Type | Integer |
| Coefficients Range | -1, 1 |
| ====== |  |
| Workflow | Iterative-Warm-Start QAOA with XY-Mixers: (1) Preprocessing fix simplicial and pendant. Identify cliques, reformulate as one-hot constraints, enforce via XY-Mixers. (2) Apply uniform warm starting, estimate QAOA angles (reps=1). (3) Build QAOA circuit and sample from QPU. (4) Greedy postprocessing on samples. (5) Estimate new warm-start probabilities, apply and continue with (3). Hyperparameters: iterations=10, parallel_runs=5, shots_per_run=500, beta=2, epsilon=0.1. (preprocess in this instance: fixed=77, cliques=[], vars=85, biases=396) |
| Algorithm Type | Stochastic |
| Paradigm | Quantum Hardware / Hybrid |
| # Runs | 5 |
| # Feasible Runs | 5 |
| # Successful Runs | 3 |
| Success Threshold | 0 |
| ====== |  |
| Hardware Specifications | Quantum: ibm_fez, Classical: MacBook Pro M5 |
| ====== |  |
| Total Runtime | 3359.46 |
| Time to Solution | N/A |
| CPU Runtime | 382.80 |
| GPU Runtime | N/A |
| QPU Runtime | 187.40 |
| Other HW Runtime | N/A |
| ====== |  |
| Remarks | Runtime in seconds. Averaged over 5 runs. QPU Runtime is session time. Idle CPU time (waiting for QPU) not counted in 'CPU Runtime'. |
