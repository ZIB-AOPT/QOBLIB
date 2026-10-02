# Submission for sloane_1dc_64

This directory contains the submission for the problem **sloane_1dc_64**.

| Field | Value 1 |
| --- | --- |
| Problem | sloane_1dc_64 |
| Submitter | Vivek Dixit,Vaibhaw Kumar, Kentaro Ohno, Alberto Maldonado Romo, Larry Bowden |
| Affiliation | IBM Research, IBM Research, IBM Research, IBM Research, Digital Woodside Energy |
| Date | 2026-09-04 |
| ====== |  |
| Reference | https://arxiv.org/abs/2609.00881 |
| Best Objective Value | 10 |
| Optimality Bound | N/A |
| ====== |  |
| Modeling Approach | QUBO |
| # Decision Variables | 64 |
| # Binary Variables | 64 |
| # Integer Variables | 0 |
| # Continuous Variables | 0 |
| # Non-Zero Coefficients | 607 |
| Coefficients Type | integer |
| Coefficients Range | {-1.0, 2.0} |
| ====== |  |
| Workflow | The solver iteratively applies classical reductions to fix provably optimal vertices, then runs hardware-aware QAOA to estimate marginal probabilities for the remaining vertices. It selects the highest-marginal vertex, adds it to the independent set, removes its closed neighborhood, and repeats on the reduced graph. When no vertices remain, the accumulated set is returned as the MIS. |
| Algorithm Type | Stochastic |
| Paradigm | Quantum Hardware |
| # Runs | 20 |
| # Feasible Runs | 20 |
| # Successful Runs | 19 |
| Success Threshold | 0.1 |
| ====== |  |
| Hardware Specifications | QPU: Heron r3 (ibm_aachen) ; CPU: VM with 32 cores and 128 GB of RAM. |
| ====== |  |
| Total Runtime | 41522.3145 |
| Time to Solution | N/A |
| CPU Runtime | 41498.3145 |
| GPU Runtime | N/A |
| QPU Runtime | 24 |
| Other HW Runtime | N/A |
| ====== |  |
| Remarks | N/A |
