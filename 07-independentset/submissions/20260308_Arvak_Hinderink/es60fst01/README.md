# Submission for es60fst01

This directory contains the submission for the problem **es60fst01**.

| Field | Value 1 |
| --- | --- |
| Problem | es60fst01 |
| Submitter | Daniel Hinderink |
| Affiliation | hiq-lab |
| Date | 2026-03-08 |
| ====== |  |
| Reference | https://arvak.io |
| Best Objective Value | N/A |
| Optimality Bound | N/A |
| ====== |  |
| Modeling Approach | QUBO |
| # Decision Variables | 123 |
| # Binary Variables | 123 |
| # Integer Variables | 0 |
| # Continuous Variables | 0 |
| # Non-Zero Coefficients | 441 |
| Coefficients Type | Integer |
| Coefficients Range | {-1; 2} |
| ====== |  |
| Workflow | 1) QUBO loaded from .qs file. 2) QAOA p=1 circuit built from QUBO terms. 3) COBYLA optimizer (23 iterations) on IBM QPU. 4) Final 4096-shot sampling. |
| Algorithm Type | Stochastic |
| Paradigm | Quantum Hardware |
| # Runs | 1 |
| # Feasible Runs | 0 |
| # Successful Runs | 0 |
| Success Threshold | 0 |
| ====== |  |
| Hardware Specifications | Apple M3 Pro and IBM Quantum ibm_torino (Heron r2 156q) |
| ====== |  |
| Total Runtime | 779 |
| Time to Solution | N/A |
| CPU Runtime | 10 |
| GPU Runtime | N/A |
| QPU Runtime | 669 |
| Other HW Runtime | N/A |
| ====== |  |
| Remarks | Runtime in seconds. 123 of 156 qubits used. Compiled with Arvak v1.9.3. The single run returned a 49-node candidate with 11 edge conflicts (infeasible per checker v2.0; see issue #82). |
