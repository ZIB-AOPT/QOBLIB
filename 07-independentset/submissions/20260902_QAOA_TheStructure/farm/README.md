# Submission for farm

This directory contains the submission for the problem **farm**.

| Field | Value 1 |
| --- | --- |
| Problem | farm |
| Submitter | Max |
| Affiliation | The Structure |
| Date | 2026-09-01 |
| ====== |  |
| Reference | Farhi, E., Goldstone, J., & Gutmann, S. (2014). A Quantum Approximate Optimization Algorithm. arXiv:1411.4028. Standard QAOA implementation; no dedicated method paper. |
| Best Objective Value | 10 |
| Optimality Bound | N/A |
| ====== |  |
| Modeling Approach | QUBO |
| # Decision Variables | 17 |
| # Binary Variables | 17 |
| # Integer Variables | N/A |
| # Continuous Variables | N/A |
| # Non-Zero Coefficients | 56 |
| Coefficients Type | Integer |
| Coefficients Range | [-2, 1] |
| ====== |  |
| Workflow | Depth-3 QAOA with COBYLA classical optimizer. 10 independent random restarts per depth level (p=1, p=2, p=3); best solution selected across all restarts and depths. 4096 shots per circuit evaluation. |
| Algorithm Type | Stochastic |
| Paradigm | Quantum Simulator |
| # Runs | 10 |
| # Feasible Runs | 10 |
| # Successful Runs | 10 |
| Success Threshold | N/A |
| ====== |  |
| Hardware Specifications | IBM Cloud VPC cx2-4x8 (4 vCPU Intel Xeon, 8 GB RAM), Qiskit Aer 0.17.2 |
| ====== |  |
| Total Runtime | 12.45 s |
| Time to Solution | N/A |
| CPU Runtime | 12.45 s |
| GPU Runtime | N/A |
| QPU Runtime | N/A |
| Other HW Runtime | N/A |
| ====== |  |
| Remarks | Objective formulated as maximization of the negated QUBO. Canonical MIS formulation: linear penalty coefficient +1 per node, edge constraint coefficient -2 per violated edge. Runtime is entirely CPU-based simulation. |
