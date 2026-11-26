# Submission for po_a200_t10_orig_b050_l1e-4

This directory contains the submission for the problem **po_a200_t10_orig_b050_l1e-4**.

| Field | Value 1 |
| --- | --- |
| Problem | po_a200_t10_orig_b050_l1e-4 |
| Submitter | Alessandro Ruzza [1], Lorenzo La Corte [1], Daniele Salvi [2] |
| Affiliation | [1] Università della Svizzera italiana (USI), [2] Politecnico di Milano |
| Date | 2026-11-26 |
| ====== |  |
| Reference | https://github.com/LorenzoLaCorte/quantum-icing-qoro |
| Best Objective Value | -794168 |
| Optimality Bound | N/A |
| ====== |  |
| Modeling Approach | QUBO (bqp_u3_c10.zpl with the equality constraints as penalties), block-sparse |
| # Decision Variables | 12100 |
| # Binary Variables | 12100 |
| # Integer Variables | 0 |
| # Continuous Variables | 0 |
| # Non-Zero Coefficients | N/A |
| Coefficients Type | Integer |
| Coefficients Range | N/A |
| ====== |  |
| Workflow | Large-neighbourhood search with PCE sub-solver (Qoro Divi): asset/time windows -> sub-QUBO solved with Pauli Correlation Encoding (9 qubits, 3 layers) -> accept if better. |
| Algorithm Type | Stochastic |
| Paradigm | Quantum Simulator |
| # Runs | 1 |
| # Feasible Runs | 1 |
| # Successful Runs | 1 |
| Success Threshold | 0 |
| ====== |  |
| Hardware Specifications | AMD Ryzen 7 4800H (8 cores / 16 threads), 9 GB RAM, Linux (WSL2); CPU only |
| ====== |  |
| Total Runtime | 3600 |
| Time to Solution | N/A |
| CPU Runtime | 3600 |
| GPU Runtime | N/A |
| QPU Runtime | N/A |
| Other HW Runtime | N/A |
| ====== |  |
| Remarks | New result (no published value). Runtime from log (9424 windows, 3,025,104 circuits). Largest circuit 9 qubits. Quantum circuits simulated on CPU with Qoro Divi (Maestro); no QPU used. |
