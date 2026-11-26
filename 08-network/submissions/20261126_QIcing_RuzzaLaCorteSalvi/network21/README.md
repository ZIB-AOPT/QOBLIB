# Submission for network21

This directory contains the submission for the problem **network21**.

| Field | Value 1 |
| --- | --- |
| Problem | network21 |
| Submitter | Alessandro Ruzza [1], Lorenzo La Corte [1], Daniele Salvi [2] |
| Affiliation | [1] Università della Svizzera italiana (USI), [2] Politecnico di Milano |
| Date | 2026-11-26 |
| ====== |  |
| Reference | https://github.com/LorenzoLaCorte/quantum-icing-qoro |
| Best Objective Value | 562362 |
| Optimality Bound | N/A |
| ====== |  |
| Modeling Approach | Binary arc variables searched directly; each topology scored by the exact min-congestion routing LP (continuous flows), final routing integral |
| # Decision Variables | 1261 |
| # Binary Variables | 420 |
| # Integer Variables | 0 |
| # Continuous Variables | 841 |
| # Non-Zero Coefficients | N/A |
| Coefficients Type | Integer |
| Coefficients Range | N/A |
| ====== |  |
| Workflow | Vertex-deletion warm starts with QAOA-sampled moves (18 qubits, Qoro Divi), then certified local search. Solution checked with QOBLIB's checker. |
| Algorithm Type | Stochastic |
| Paradigm | Quantum Simulator |
| # Runs | 1 |
| # Feasible Runs | 1 |
| # Successful Runs | 1 |
| Success Threshold | 0 |
| ====== |  |
| Hardware Specifications | AMD Ryzen 7 4800H (8 cores / 16 threads), 9 GB RAM, Linux (WSL2); CPU only |
| ====== |  |
| Total Runtime | 270 |
| Time to Solution | N/A |
| CPU Runtime | 270 |
| GPU Runtime | N/A |
| QPU Runtime | N/A |
| Other HW Runtime | N/A |
| ====== |  |
| Remarks | Below QOBLIB best known 569273. Chain step 270 s (from log). Quantum circuits simulated on CPU with Qoro Divi (Maestro); no QPU used. |
