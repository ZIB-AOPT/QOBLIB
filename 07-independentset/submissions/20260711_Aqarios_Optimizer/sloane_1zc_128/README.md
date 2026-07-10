# Submission for sloane_1zc_128
This directory contains the submission for the problem **sloane_1zc_128**
| Field | Value 1 |
| --- | --- |
| Problem | `sloane_1zc_128` |
| Submitter | David Bucher |
| Affiliation | Aqarios GmbH |
| Date | 2026-07-11 00:44:13 |
| ====== |  |
| Reference | Paper: https://arxiv.org/pdf/2604.02083. In the process of becoming a Qiskit Function |
| Best Objective Value | 18 |
| Optimality Bound | N/A |
| ====== |  |
| Modeling Approach | Binary Linear Program |
| # Decision Variables | 128 |
| # Binary Variables | 128 |
| # Integer Variables | N/A |
| # Continuous Variables | N/A |
| # Non-Zero Coefficients | 2368 |
| Coefficients Type | Integer |
| Coefficients Range | -1, 1 |
| ====== |  |
| Workflow | Iterative-Warm-Start QAOA with XY-Mixers: (1) Preprocessing fix simplicial and pendant. Identify cliques, reformulate as one-hot constraints, enforce via XY-Mixers. (2) Apply uniform warm starting, estimate QAOA angles (reps=1). (3) Build QAOA circuit and sample from QPU. (4) Greedy postprocessing on samples. (5) Estimate new warm-start probabilities, apply and continue with (3). Hyperparameters: iterations=10, parallel_runs=5, shots_per_run=500, beta=2, epsilon=0.1. (preprocess in this instance: fixed=16, cliques=[6, 6, 6, 6, 6, 6, 6, 6, 5, 5, 5, 4, 4, 4, 4, 4, 4, 4, 4], vars=131, biases=2365) |
| Algorithm Type | Stochastic |
| Paradigm | Quantum Hardware / Hybrid |
| # Runs | 5 |
| # Feasible Runs | 5 |
| # Successful Runs | 5 |
| Success Threshold | 0 |
| ====== |  |
| Hardware Specifications | Quantum: ibm_fez, Classical: MacBook Pro M5 |
| ====== |  |
| Total Runtime | 3671.73 |
| Time to Solution | N/A |
| CPU Runtime | 423.13 |
| GPU Runtime | N/A |
| QPU Runtime | 282.40 |
| Other HW Runtime | N/A |
| ====== |  |
| Remarks | Runtime in seconds. Averaged over 5 runs. QPU Runtime is session time. Idle CPU time (waiting for QPU) not counted in 'CPU Runtime'. |
