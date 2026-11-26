# Submission for network24

This directory contains the submission for the problem **network24**.

| Field | Value 1 |
| --- | --- |
| Problem | network24 |
| Submitter | Alessandro Ruzza [1], Lorenzo La Corte [1], Daniele Salvi [2] |
| Affiliation | [1] Università della Svizzera italiana (USI), [2] Politecnico di Milano |
| Date | 2026-11-26 |
| ====== |  |
| Reference | https://github.com/LorenzoLaCorte/quantum-icing-qoro |
| Best Objective Value | 657121 |
| Optimality Bound | N/A |
| ====== |  |
| Modeling Approach | Binary arc variables searched directly; each topology scored by the exact min-congestion routing LP (continuous flows), final routing integral |
| # Decision Variables | 1657 |
| # Binary Variables | 552 |
| # Integer Variables | 0 |
| # Continuous Variables | 1105 |
| # Non-Zero Coefficients | N/A |
| Coefficients Type | Integer |
| Coefficients Range | N/A |
| ====== |  |
| Workflow | Parallel tempering and ILS. Solution checked with QOBLIB's checker. |
| Algorithm Type | Stochastic |
| Paradigm | Classical |
| # Runs | 1 |
| # Feasible Runs | 1 |
| # Successful Runs | 1 |
| Success Threshold | 0 |
| ====== |  |
| Hardware Specifications | AMD Ryzen 7 4800H (8 cores / 16 threads), 9 GB RAM, Linux (WSL2); CPU only |
| ====== |  |
| Total Runtime | 4232 |
| Time to Solution | N/A |
| CPU Runtime | 4232 |
| GPU Runtime | N/A |
| QPU Runtime | N/A |
| Other HW Runtime | N/A |
| ====== |  |
| Remarks | Below QOBLIB best known 663688. PT 1802 s, ILS 1229 s, PT 1201 s (from logs). |
