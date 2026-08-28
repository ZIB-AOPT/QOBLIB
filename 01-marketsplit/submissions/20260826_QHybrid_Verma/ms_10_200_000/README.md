# Submission for ms_10_200_000

This directory contains the submission for the problem ms_10_200_000.

| Field | Value 1 |
| --- | --- |
| Problem | ms_10_200_000 |
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
| # Non-Zero Coefficients | 898 |
| Coefficients Type | Integer |
| Coefficients Range | 1 - 198 |
| ====== |  |
| Workflow | Lattice-based pre-conditioning, followed by a variational quantum sampling circuit, with classical post-processing. |
| Algorithm Type | Stochastic |
| Paradigm | Quantum Hardware |
| # Runs | 1 |
| # Feasible Runs | 1 |
| # Successful Runs | 1 |
| Success Threshold | 0 |
| ====== |  |
| Hardware Specifications | Quantum: ibm_aachen (IBM Heron r3, 156 qubits), Qiskit Runtime session mode; 16384 shots for the read-out used to produce the submitted solution. Classical: Apple M4 Max, 16 cores, 64 GB RAM, macOS 15.7.4; Python 3.14.3, Qiskit 2.4.2, qiskit-ibm-runtime 0.47.0, fpylll 0.6.4. |
| ====== |  |
| Total Runtime | 297.88 |
| Time to Solution | 297.88 |
| CPU Runtime | 224.12 |
| GPU Runtime | N/A |
| QPU Runtime | 73.76 |
| Other HW Runtime | N/A |
| ====== |  |
| Remarks | Objective is the market-split violation |Ax-b|; 0 = feasible. Quantum read-out taken on ibm_aachen using 72 qubits. QPU Runtime follows the QOBLIB definition (Qiskit Runtime session mode; queue time excluded; inter-job idle attributed to classical runtime): 9 jobs, 552s of queue excluded; IBM-reported 'actual usage' for the same jobs is 31s. Runtimes are for the single reported configuration; hyperparameter and basis-search time is not included. |
