# Submission for ms_10_200_001

This directory contains the submission for the problem ms_10_200_001.

| Field | Value 1 |
| --- | --- |
| Problem | ms_10_200_001 |
| Submitter | Dhriti Verma, Kalyan Dasgupta, Dzung Phan, Jayant Kalagnanam |
| Affiliation | IBM, IBM, IBM, IBM |
| Date | 2026-08-26 |
| ====== |  |
| Reference | N/A |
| Best Objective Value | 0.0 |
| Optimality Bound | 0.0 |
| ====== |  |
| Modeling Approach | Integer lattice reformulation of Ax=b. |
| # Decision Variables | 90 |
| # Binary Variables | 90 |
| # Integer Variables | N/A |
| # Continuous Variables | N/A |
| # Non-Zero Coefficients | 896 |
| Coefficients Type | Integer |
| Coefficients Range | 1 - 198 |
| ====== |  |
| Workflow | Lattice-based pre-conditioning, followed by a variational quantum sampling circuit, with classical post-processing. |
| Algorithm Type | Stochastic |
| Paradigm | Quantum Hardware |
| # Runs | 5 |
| # Feasible Runs | 3 |
| # Successful Runs | 3 |
| Success Threshold | 0 |
| ====== |  |
| Hardware Specifications | Quantum: ibm_aachen (IBM Heron r3, 156 qubits), Qiskit Runtime session mode; 65536 shots for the read-out used to produce the submitted solution. Classical: Apple M4 Max, 16 cores, 64 GB RAM, macOS 15.7.4; Python 3.14.3, Qiskit 2.4.2, qiskit-ibm-runtime 0.47.0, fpylll 0.6.4. |
| ====== |  |
| Total Runtime | 243.97 |
| Time to Solution | 243.97 |
| CPU Runtime | 131.14 |
| GPU Runtime | N/A |
| QPU Runtime | 112.83 |
| Other HW Runtime | N/A |
| ====== |  |
| Remarks | Objective is the market-split constraint violation; 0 = feasible. Quantum read-out taken on ibm_aachen. Total Runtime, CPU Runtime and QPU Runtime are averages across the 3 successful runs of 5 (a successful run is one that reached the best objective, 0). QPU Runtime follows the QOBLIB definition (Qiskit Runtime session mode; queue time excluded; inter-job idle attributed to classical runtime); IBM-reported 'actual usage' per run for the same jobs is 67s. Hyperparameter and basis-search time is not included. |
