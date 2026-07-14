# Submission for es60fst02
This directory contains the submission for the problem **es60fst02**
| Field | Value 1 |
| --- | --- |
| Problem | `es60fst02` |
| Submitter | David Bucher |
| Affiliation | Aqarios GmbH |
| Date | 2026-07-11 00:52:04 |
| ====== |  |
| Reference | Paper: https://arxiv.org/pdf/2604.02083. In the process of becoming a Qiskit Function |
| Best Objective Value | 88 |
| Optimality Bound | N/A |
| ====== |  |
| Modeling Approach | Binary Linear Program |
| # Decision Variables | 186 |
| # Binary Variables | 186 |
| # Integer Variables | N/A |
| # Continuous Variables | N/A |
| # Non-Zero Coefficients | 746 |
| Coefficients Type | Integer |
| Coefficients Range | -1, 1 |
| ====== |  |
| Workflow | Iterative-Warm-Start QAOA with XY-Mixers: (1) Preprocessing fix simplicial and pendant. Identify cliques, reformulate as one-hot constraints, enforce via XY-Mixers. (2) Apply uniform warm starting, estimate QAOA angles (reps=1). (3) Build QAOA circuit and sample from QPU. (4) Greedy postprocessing on samples. (5) Estimate new warm-start probabilities, apply and continue with (3). Hyperparameters: iterations=10, parallel_runs=5, shots_per_run=500, beta=2, epsilon=0.1. (preprocess in this instance: fixed=62, cliques=[], vars=124, biases=579) |
| Algorithm Type | Stochastic |
| Paradigm | Quantum Hardware / Hybrid |
| # Runs | 5 |
| # Feasible Runs | 5 |
| # Successful Runs | 4 |
| Success Threshold | 0 |
| ====== |  |
| Hardware Specifications | Quantum: ibm_fez, Classical: MacBook Pro M5 |
| ====== |  |
| Total Runtime | 240.09 |
| Time to Solution | 131.14 |
| CPU Runtime | 22.00 |
| GPU Runtime | N/A |
| QPU Runtime | 215.00 |
| Other HW Runtime | N/A |
| ====== |  |
| Remarks | Runtime in seconds. Averaged over 5 runs. QPU Runtime is session time. Idle CPU time (waiting for QPU) not counted in 'CPU Runtime'. Average iterations to solution 5.25 (successful runs only). |
