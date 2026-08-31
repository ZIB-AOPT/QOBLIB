# Submission for C125-9

This directory contains the submission for the problem **C125-9**.

| Field | Value 1 |
| --- | --- |
| Problem | C125-9 |
| Submitter | Kalyan Dasgupta, Sumanta Mukherjee, Dhriti Verma, Surya Shravan Kumar Sajja, Abhishek Singh, Dzung Phan, Jayant Kalagnanam |
| Affiliation | IBM Research - Bangalore - India, IBM Research - Bangalore - India, IBM Research - Yorktown Heights - NY - USA, IBM Research - Bangalore - India, IBM Research - Bangalore - India, IBM Research - Yorktown Heights - NY - USA, IBM Research - Yorktown Heights - NY - USA |
| Date | 2026-08-31 |
| ====== |  |
| Reference | https://arxiv.org/abs/2606.28866 |
| Best Objective Value | 34 |
| Optimality Bound | N/A |
| ====== |  |
| Modeling Approach | Ising Hamiltonian from QUBO relaxation (max sum_i x_i - P*sum_(i,j) in E x_i x_j); spectral (Fiedler) qubit reordering + distance-based sparsification of long-range couplings before circuit construction |
| # Decision Variables | 125 |
| # Binary Variables | 125 |
| # Integer Variables | 0 |
| # Continuous Variables | 0 |
| # Non-Zero Coefficients | 912 |
| Coefficients Type | Continuous |
| Coefficients Range | J_ij = P/4 (constant over edges); h_i = 0.5 - P*deg_i/4 (varies with node degree); P (penalty) = 2.0 for this run |
| ====== |  |
| Workflow | Build Ising Hamiltonian from graph; spectral reordering; sparsify couplings (max_adj); train EfficientSU2 VQE ansatz (n_reps=2, 750 parameters) with COBYLA and CVaR (alpha=0.2, initial params = zeros) using AerSimulator (MPS method) for parameter optimization; transfer optimized parameters to ibm_marrakesh hardware for final circuit sampling; post-process samples with greedy bitstring repair and local-search based bitstring correction to extract maximal independent sets. |
| Algorithm Type | Stochastic |
| Paradigm | Quantum Hardware |
| # Runs | 10 |
| # Feasible Runs | 10 |
| # Successful Runs | 10 |
| Success Threshold | 0 |
| ====== |  |
| Hardware Specifications | Classical: MacBook Pro (MacBookPro18,1), Apple M1 Pro, 10 cores (8 performance + 2 efficiency), 32 GB RAM, macOS, used for VQE parameter training via AerSimulator (MPS method). Quantum: IBM Quantum ibm_marrakesh (Heron) via Qiskit Runtime, 20000 shots/trial x 10 trials. |
| ====== |  |
| Total Runtime | 2283.73 |
| Time to Solution | N/A |
| CPU Runtime | 1101.58 |
| GPU Runtime | N/A |
| QPU Runtime | 8 |
| Other HW Runtime | N/A |
| ====== |  |
| Remarks | NOTE ON '# Successful Runs': all 10 sampling trials' raw bitstrings are pooled and deduplicated together before the final best independent set is extracted, so no single trial alone reaches the reported best size. It is a joint result of all trials. Individual per-trial raw-sample size is not predictive of final MIS quality, since smaller seeds can extend further under maximality-driving (local search); additionally, per our reference paper, the bitstring-correction heuristic uses an EMA that improves across successive trials, so later trials are more likely to yield the MIS than earlier ones. The trials are not i.i.d. and cannot be scored independently. '# Successful Runs' = 10 reflects that all trials contributed feasible samples to this pooled, cumulative outcome, not that each trial individually matched the best size. PARAMETER TRANSFER RUN: VQE parameters were trained entirely classically via simulator (AerSimulator MPS); no training occurred on hardware. The trained parameters were then transferred as-is to run the fixed circuit on real IBM Quantum hardware (ibm_marrakesh) for sampling only. Total Runtime = 1101.58s classical VQE parameter optimization (AerSimulator MPS) + 1182.15s post-optimization hardware sampling/bitstring correction on ibm_marrakesh. QPU Runtime (8s) is the average actual quantum execution time per sampling round (10 rounds x 8s/round), excluding queue time; the remainder of the hardware phase is classical post-processing (bitstring repair/local search). We report not only that the optimal independent set (size 34, matching QOBLIB's best-known value) was recovered, but how many distinct maximum-size sets were found: out of 2903 total unique independent sets extracted from 10 hardware sampling trials (20000 shots each) after bitstring correction, 4 distinct sets of the maximum size (34) were recovered. To our knowledge this multiplicity-of-optima reporting has not been done elsewhere for this instance. |
