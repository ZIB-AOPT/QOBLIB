# Submission for johnson8-2-4

This directory contains the submission for the problem **johnson8-2-4**.

| Field | Value 1 |
| --- | --- |
| Problem | johnson8-2-4 |
| Submitter | Dzung Phan, Vinicius Lima, Jayant Kalagnanam |
| Affiliation | IBM, IBM, IBM |
| Date | 2026-11-24 |
| ====== |  |
| Reference | N/A |
| Best Objective Value | 7 |
| Optimality Bound | N/A |
| ====== |  |
| Modeling Approach | MIS binary LP -> exact reduction -> clique-cover QAOA encoding |
| # Decision Variables | 28 |
| # Binary Variables | 28 |
| # Integer Variables | 0 |
| # Continuous Variables | 0 |
| # Non-Zero Coefficients | 448 |
| Coefficients Type | Integer |
| Coefficients Range | 1 to 1 |
| ====== |  |
| Workflow | Exact graph reductions; fixed-angle QAOA with clique encoding; classical postprocessing. |
| Algorithm Type | Stochastic |
| Paradigm | Quantum Hardware |
| # Runs | 5 |
| # Feasible Runs | 5 |
| # Successful Runs | 5 |
| Success Threshold | 0 |
| ====== |  |
| Hardware Specifications | IBM Quantum ibm_boston, 156 physical qubits available, 35 encoded qubits; MacBookPro18,2, Apple M1 Max, 10 CPU cores, 64 GB RAM, macOS 26.6.2 |
| ====== |  |
| Total Runtime | 1.839475 |
| Time to Solution | 1.839475 |
| CPU Runtime | 0.427683 |
| GPU Runtime | N/A |
| QPU Runtime | 1.411792 |
| Other HW Runtime | N/A |
| ====== |  |
| Remarks | QPU Runtime is circuit execution time (IBM circuits_execution_time_ns converted to seconds). Mean billed QPU time: 4.000000 s. Total Runtime and Time to Solution equal CPU Runtime plus QPU Runtime. Compilation and queue time are excluded. |
