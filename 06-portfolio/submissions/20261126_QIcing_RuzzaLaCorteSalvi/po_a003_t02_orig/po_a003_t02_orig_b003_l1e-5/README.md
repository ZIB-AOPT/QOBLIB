# Submission for po_a003_t02_orig_b003_l1e-5

This directory contains the submission for the problem **po_a003_t02_orig_b003_l1e-5**.

| Field | Value 1 |
| --- | --- |
| Problem | po_a003_t02_orig_b003_l1e-5 |
| Submitter | Alessandro Ruzza [1], Lorenzo La Corte [1], Daniele Salvi [2] |
| Affiliation | [1] Università della Svizzera italiana (USI), [2] Politecnico di Milano |
| Date | 2026-11-26 |
| ====== |  |
| Reference | https://github.com/LorenzoLaCorte/quantum-icing-qoro |
| Best Objective Value | -2505 |
| Optimality Bound | -2505 |
| ====== |  |
| Modeling Approach | Integer quadratic program on net positions v = long - short in {-3..3} per asset and period (equivalent to bqp_u3_c10.zpl) |
| # Decision Variables | 6 |
| # Binary Variables | 0 |
| # Integer Variables | 6 |
| # Continuous Variables | 0 |
| # Non-Zero Coefficients | N/A |
| Coefficients Type | Integer |
| Coefficients Range | N/A |
| ====== |  |
| Workflow | Exact dynamic programming over trading days (all feasible daily positions enumerated). Proven optimal. |
| Algorithm Type | Deterministic |
| Paradigm | Classical |
| # Runs | 1 |
| # Feasible Runs | 1 |
| # Successful Runs | 1 |
| Success Threshold | 0 |
| ====== |  |
| Hardware Specifications | AMD Ryzen 7 4800H (8 cores / 16 threads), 9 GB RAM, Linux (WSL2); CPU only |
| ====== |  |
| Total Runtime | 1 |
| Time to Solution | 1 |
| CPU Runtime | 1 |
| GPU Runtime | N/A |
| QPU Runtime | N/A |
| Other HW Runtime | N/A |
| ====== |  |
| Remarks | New result (no published value). Runtime estimated (seconds). |
