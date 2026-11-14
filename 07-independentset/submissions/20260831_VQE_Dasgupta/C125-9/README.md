# Submission for C125-9

This directory contains the submission for the problem **C125-9**.

| Field | Value 1 | Value 2 |
| --- | --- | --- |
| Problem | C125-9 | C125-9 |
| Submitter | Kalyan Dasgupta, Sumanta Mukherjee, Dhriti Verma, Surya Shravan Kumar Sajja, Abhishek Singh, Dzung Phan, Jayant Kalagnanam | Kalyan Dasgupta, Sumanta Mukherjee, Dhriti Verma, Surya Shravan Kumar Sajja, Abhishek Singh, Dzung Phan, Jayant Kalagnanam |
| Affiliation | IBM Research - Bangalore - India, IBM Research - Bangalore - India, IBM Research - Yorktown Heights - NY - USA, IBM Research - Bangalore - India, IBM Research - Bangalore - India, IBM Research - Yorktown Heights - NY - USA, IBM Research - Yorktown Heights - NY - USA | IBM Research - Bangalore - India, IBM Research - Bangalore - India, IBM Research - Yorktown Heights - NY - USA, IBM Research - Bangalore - India, IBM Research - Bangalore - India, IBM Research - Yorktown Heights - NY - USA, IBM Research - Yorktown Heights - NY - USA |
| Date | 2026-08-31 | 2026-08-31 |
| ====== |  |  |
| Reference | https://arxiv.org/abs/2606.28866 | https://arxiv.org/abs/2606.28866 |
| Best Objective Value | 34 | 34 |
| Optimality Bound | N/A | N/A |
| ====== |  |  |
| Modeling Approach | Ising Hamiltonian from QUBO relaxation (max sum_i x_i - P*sum_(i,j) in E x_i x_j); spectral (Fiedler) qubit reordering + distance-based sparsification of long-range couplings before circuit construction | Ising Hamiltonian from QUBO relaxation (max sum_i x_i - P*sum_(i,j) in E x_i x_j); spectral (Fiedler) qubit reordering + distance-based sparsification of long-range couplings before circuit construction |
| # Decision Variables | 125 | 125 |
| # Binary Variables | 125 | 125 |
| # Integer Variables | 0 | 0 |
| # Continuous Variables | 0 | 0 |
| # Non-Zero Coefficients | 912 | 912 |
| Coefficients Type | Continuous | Continuous |
| Coefficients Range | J_ij = P/4 (constant over edges); h_i = 0.5 - P*deg_i/4 (varies with node degree); P (penalty) = 2.0 for this run | J_ij = P/4 (constant over edges); h_i = 0.5 - P*deg_i/4 (varies with node degree); P (penalty) = 2.0 for this run |
| ====== |  |  |
| Workflow | Build Ising Hamiltonian from graph; spectral reordering; sparsify couplings (max_adj); train EfficientSU2 VQE ansatz (n_reps=2, 750 parameters) with COBYLA and CVaR (alpha=0.2, initial params = zeros) using AerSimulator (MPS method) for parameter optimization; transfer optimized parameters to ibm_marrakesh hardware for final circuit sampling; post-process samples with greedy bitstring repair and local-search based bitstring correction to extract maximal independent sets. | Build Ising Hamiltonian from graph; spectral reordering; sparsify couplings (max_adj); train EfficientSU2 VQE ansatz (n_reps=2, 750 parameters) with COBYLA and CVaR (alpha=0.2, initial params = zeros) using AerSimulator (MPS method); post-process samples (100000 shots/trial x 10 trials) with greedy bitstring repair and local-search based bitstring correction to extract maximal independent sets. |
| Algorithm Type | Stochastic | Stochastic |
| Paradigm | Quantum Hardware | Quantum Simulator |
| # Runs | 3 | 5 |
| # Feasible Runs | 3 | 5 |
| # Successful Runs | 2 | 5 |
| Success Threshold | N/A | N/A |
| ====== |  |  |
| Hardware Specifications | Classical: MacBook Pro, Apple M1 Pro, 10 cores (8 performance + 2 efficiency), 32 GB RAM, macOS, used for VQE parameter training via AerSimulator (MPS method). Quantum: IBM Quantum ibm_marrakesh (Heron) via Qiskit Runtime, 20000 shots/trial x 10 trials. | MacBook Pro, Apple M1 Pro, 10 cores (8 performance + 2 efficiency), 32 GB RAM, macOS, using AerSimulator (MPS method). |
| ====== |  |  |
| Total Runtime | 1489.21 | 1023.63 |
| Time to Solution | N/A | N/A |
| CPU Runtime | N/A | N/A |
| GPU Runtime | N/A | N/A |
| QPU Runtime | 8 | N/A |
| Other HW Runtime | N/A | N/A |
| ====== |  |  |
| Remarks | TIMING NOTE: we did not measure CPU-process time (e.g. via time.process_time()) or log CPU utilization separately; only wall-clock time (via time.time()) was recorded, so 'CPU Runtime' is left as N/A and the full wall-clock duration is reported under 'Total Runtime' instead. NOTE ON '# Runs': we report 3 runs (# Runs = 3); each run pools several measurement-shot batches before extracting the best independent set, as described in our reference paper (arXiv:2606.28866). Total Runtime (1489.21s) is the average of these 3 runs' wall-clock times, per CONTRIBUTING.md guidance to report averages across repetitions. PARAMETER TRANSFER RUN: VQE parameters were trained via classical simulation (AerSimulator MPS) and transferred to real IBM Quantum hardware (ibm_marrakesh) for sampling only; no training occurred on hardware. QPU Runtime (8s) is the average actual quantum execution time, excluding queue time. All 3 runs produced feasible solutions ('# Feasible Runs' = 3), and 2 of the 3 reached the optimum, size 34, matching QOBLIB's best-known value ('# Successful Runs' = 2). 166 distinct maximum-size (34) independent sets have been found across all runs to date (combining this row with the Quantum Simulator row below), all provided as separate files in the solutions/ directory, each tagged with a '# Origin' comment line indicating which row it came from. | TIMING NOTE: we did not measure CPU-process time (e.g. via time.process_time()) or log CPU utilization separately; only wall-clock time (via time.time()) was recorded, so 'CPU Runtime' is left as N/A and the full wall-clock duration is reported under 'Total Runtime' instead. NOTE ON '# Runs': we report 5 runs (# Runs = 5); each run pools several measurement-shot batches before extracting the best independent set, as described in our reference paper (arXiv:2606.28866). Total Runtime (1023.63s) is the average of these 5 runs' wall-clock times, per CONTRIBUTING.md guidance to report averages across repetitions. All 5 runs recovered the optimal independent set, size 34, matching QOBLIB's best-known value ('# Feasible Runs' = '# Successful Runs' = 5). 166 distinct maximum-size (34) independent sets have been found across all runs to date (combining this row with the Quantum Hardware row above), all provided as separate files in the solutions/ directory, each tagged with a '# Origin' comment line indicating which row it came from. |
