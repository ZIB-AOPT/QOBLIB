# Submission for po_a200_t10_orig_b050_l5e-4

This directory contains the submission for the problem **po_a200_t10_orig_b050_l5e-4**.

| Field | Value 1 |
| --- | --- |
| Problem | po_a200_t10_orig_b050_l5e-4 |
| Submitter | Alessandro Ruzza [1], Lorenzo La Corte [1], Daniele Salvi [2] |
| Affiliation | [1] Università della Svizzera italiana (USI), [2] Politecnico di Milano |
| Date | 2026-11-26 |
| ====== |  |
| Reference | https://github.com/LorenzoLaCorte/quantum-icing-qoro |
| Best Objective Value | -883755 |
| Optimality Bound | N/A |
| ====== |  |
| Modeling Approach | Integer quadratic program on net positions v = long - short in {-3..3} per asset and period (equivalent to bqp_u3_c10.zpl) |
| # Decision Variables | 2000 |
| # Binary Variables | 0 |
| # Integer Variables | 2000 |
| # Continuous Variables | 0 |
| # Non-Zero Coefficients | N/A |
| Coefficients Type | Integer |
| Coefficients Range | N/A |
| ====== |  |
| Workflow | Tabu search with dynamic-programming recombination over trading days. |
| Algorithm Type | Stochastic |
| Paradigm | Classical |
| # Runs | 1 |
| # Feasible Runs | 1 |
| # Successful Runs | 1 |
| Success Threshold | 0 |
| ====== |  |
| Hardware Specifications | AMD Ryzen 7 4800H (8 cores / 16 threads), 9 GB RAM, Linux (WSL2); CPU only |
| ====== |  |
| Total Runtime | 1800 |
| Time to Solution | N/A |
| CPU Runtime | 10800 |
| GPU Runtime | N/A |
| QPU Runtime | N/A |
| Other HW Runtime | N/A |
| ====== |  |
| Remarks | New result (no published value). Runtimes in seconds, estimated from the run settings (not timed end to end). 6 parallel workers. |
