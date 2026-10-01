# Submission for farm

This directory contains the submission for the problem **farm**.

| Field | Value 1 |
| --- | --- |
| Problem | farm |
| Submitter | Daniel Hinderink |
| Affiliation | hiq-lab |
| Date | 2026-03-08 |
| ====== |  |
| Reference | https://arvak.io |
| Best Objective Value | -10 |
| Optimality Bound | -10 |
| ====== |  |
| Modeling Approach | QUBO |
| # Decision Variables | 17 |
| # Binary Variables | 17 |
| # Integer Variables | 0 |
| # Continuous Variables | 0 |
| # Non-Zero Coefficients | 95 |
| Coefficients Type | Integer |
| Coefficients Range | {-1; 2} |
| ====== |  |
| Workflow | PCE dense: 17 vars -> 5 qubits. COBYLA + statevector sim (2048 shots/eval). |
| Algorithm Type | Stochastic |
| Paradigm | Quantum Simulator |
| # Runs | 1 |
| # Feasible Runs | 1 |
| # Successful Runs | 1 |
| Success Threshold | 0 |
| ====== |  |
| Hardware Specifications | Apple M3 Pro (statevector simulation) |
| ====== |  |
| Total Runtime | 0.4 |
| Time to Solution | N/A |
| CPU Runtime | 0.4 |
| GPU Runtime | N/A |
| QPU Runtime | N/A |
| Other HW Runtime | N/A |
| ====== |  |
| Remarks | Optimal solution verified by brute-force. 3.4x qubit compression. Arvak v1.9.3. |
