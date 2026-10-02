# Submission for es60fst04

This directory contains the submission for the problem **es60fst04**.

| Field | Value 1 |
| --- | --- |
| Problem | es60fst04 |
| Submitter | Vivek Dixit,Vaibhaw Kumar, Kentaro Ohno, Alberto Maldonado Romo, Larry Bowden |
| Affiliation | IBM Research, IBM Research, IBM Research, IBM Research, Digital Woodside Energy |
| Date | 2026-09-04 |
| ====== |  |
| Reference | https://arxiv.org/abs/2609.00881 |
| Best Objective Value | 78 |
| Optimality Bound | N/A |
| ====== |  |
| Modeling Approach | QUBO |
| # Decision Variables | 162 |
| # Binary Variables | 162 |
| # Integer Variables | 0 |
| # Continuous Variables | 0 |
| # Non-Zero Coefficients | 400 |
| Coefficients Type | continuous |
| Coefficients Range | {-1.0, 1.2} |
| ====== |  |
| Workflow | The solver iteratively applies classical reductions to fix provably optimal vertices, then runs hardware-aware QAOA to estimate marginal probabilities for the remaining vertices. It selects the highest-marginal vertex, adds it to the independent set, removes its closed neighborhood, and repeats on the reduced graph. When no vertices remain, the accumulated set is returned as the MIS. |
| Algorithm Type | Stochastic |
| Paradigm | Quantum Hardware |
| # Runs | 10 |
| # Feasible Runs | 10 |
| # Successful Runs | 10 |
| Success Threshold | 0.05 |
| ====== |  |
| Hardware Specifications | QPU: Heron r3 (ibm_aachen) ; CPU: VM with 32 cores and 128 GB of RAM. |
| ====== |  |
| Total Runtime | 21508.3518 |
| Time to Solution | N/A |
| CPU Runtime | 21444.3518 |
| GPU Runtime | N/A |
| QPU Runtime | 64 |
| Other HW Runtime | N/A |
| ====== |  |
| Remarks | N/A |