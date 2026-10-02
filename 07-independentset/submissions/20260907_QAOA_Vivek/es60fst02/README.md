# Submission for es60fst02

This directory contains the submission for the problem **es60fst02**.

| Field | Value 1 |
| --- | --- |
| Problem | es60fst02 |
| Submitter | Vivek Dixit,Vaibhaw Kumar, Kentaro Ohno, Alberto Maldonado Romo, Larry Bowden |
| Affiliation | IBM Research, IBM Research, IBM Research, IBM Research, Digital Woodside Energy |
| Date | 2026-09-04 |
| ====== |  |
| Reference | https://arxiv.org/abs/2609.00881 |
| Best Objective Value | 88 |
| Optimality Bound | N/A |
| ====== |  |
| Modeling Approach | QUBO |
| # Decision Variables | 186 |
| # Binary Variables | 186 |
| # Integer Variables | 0 |
| # Continuous Variables | 0 |
| # Non-Zero Coefficients | 466 |
| Coefficients Type | integer |
| Coefficients Range | {-1.0, 2.0} |
| ====== |  |
| Workflow | The solver iteratively applies classical reductions to fix provably optimal vertices, then runs hardware-aware QAOA to estimate marginal probabilities for the remaining vertices. It selects the highest-marginal vertex, adds it to the independent set, removes its closed neighborhood, and repeats on the reduced graph. When no vertices remain, the accumulated set is returned as the MIS. |
| Algorithm Type | Stochastic |
| Paradigm | Quantum Hardware |
| # Runs | 20 |
| # Feasible Runs | 20 |
| # Successful Runs | 20 |
| Success Threshold | 0.05 |
| ====== |  |
| Hardware Specifications | QPU: Heron r3 (ibm_aachen) ; CPU: VM with 32 cores and 128 GB of RAM. |
| ====== |  |
| Total Runtime | 23365.8542 |
| Time to Solution | N/A |
| CPU Runtime | 23287.8542 |
| GPU Runtime | N/A |
| QPU Runtime | 78 |
| Other HW Runtime | N/A |
| ====== |  |
| Remarks | N/A |
