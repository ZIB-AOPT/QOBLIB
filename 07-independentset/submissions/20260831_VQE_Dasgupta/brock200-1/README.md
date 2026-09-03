# Submission for brock200-1

This directory contains the submission for the problem **brock200-1**.

| Field | Value 1 |
| --- | --- |
| Problem | brock200-1 |
| Submitter | Kalyan Dasgupta, Sumanta Mukherjee, Dhriti Verma, Surya Shravan Kumar Sajja, Abhishek Singh, Dzung Phan, Jayant Kalagnanam |
| Affiliation | IBM Research - Bangalore - India, IBM Research - Bangalore - India, IBM Research - Yorktown Heights - NY - USA, IBM Research - Bangalore - India, IBM Research - Bangalore - India, IBM Research - Yorktown Heights - NY - USA, IBM Research - Yorktown Heights - NY - USA |
| Date | 2026-08-31 |
| ====== |  |
| Reference | https://arxiv.org/abs/2606.28866 |
| Best Objective Value | 6 |
| Optimality Bound | N/A |
| ====== |  |
| Modeling Approach | Ising Hamiltonian from QUBO relaxation (max sum_i x_i - P*sum_(i,j) in E x_i x_j); spectral (Fiedler) qubit reordering + distance-based sparsification of long-range couplings before circuit construction |
| # Decision Variables | 200 |
| # Binary Variables | 200 |
| # Integer Variables | 0 |
| # Continuous Variables | 0 |
| # Non-Zero Coefficients | 15034 |
| Coefficients Type | Continuous |
| Coefficients Range | J_ij = P/4 (constant over edges); h_i = 0.5 - P*deg_i/4 (varies with node degree); P (penalty) = 2.0 for this run |
| ====== |  |
| Workflow | Build Ising Hamiltonian from graph; spectral reordering; sparsify couplings (max_adj); train EfficientSU2 VQE ansatz (n_reps=2, 1200 parameters) with SPSA and CVaR using AerSimulator (MPS method); post-process samples (100000 shots/trial x 10 trials) with greedy bitstring repair and local-search based bitstring correction to extract maximal independent sets. |
| Algorithm Type | Stochastic |
| Paradigm | Quantum Simulator |
| # Runs | 1 |
| # Feasible Runs | 1 |
| # Successful Runs | 1 |
| Success Threshold | N/A |
| ====== |  |
| Hardware Specifications | MacBook Pro (MacBookPro18,1), Apple M1 Pro, 10 cores (8 performance + 2 efficiency), 32 GB RAM, macOS, using AerSimulator (MPS method). |
| ====== |  |
| Total Runtime | 8592 |
| Time to Solution | N/A |
| CPU Runtime | N/A |
| GPU Runtime | N/A |
| QPU Runtime | N/A |
| Other HW Runtime | N/A |
| ====== |  |
| Remarks | TIMING NOTE: we did not measure CPU-process time (e.g. via time.process_time()) or log CPU utilization separately; only wall-clock time (via time.time()) was recorded, so 'CPU Runtime' is left as N/A and the full wall-clock duration is reported under 'Total Runtime' instead. NOTE ON '# Runs': this experiment is a single run (# Runs = 1): one classically-trained VQE circuit (one fixed set of optimized parameters) whose measurement shots were collected across 10 sub-batches (a practical choice for hardware/queue management) and pooled together before classical bitstring correction. The 10 sub-batches are not independent executions of the algorithm, so we do not report them as separate runs. Individual per-batch raw-sample size is not predictive of final MIS quality, since smaller seeds can extend further under maximality-driving (local search); additionally, per our reference paper, the bitstring-correction heuristic uses an EMA that improves cumulatively as more batches are pooled, so later batches benefit from more accumulated signal than earlier ones. '# Feasible Runs' = '# Successful Runs' = 1 reflects that this single pooled campaign produced the reported result, not that 10 independent attempts each succeeded. Total Runtime = 143.2 minutes (8592s): 140.8 minutes (8448s) VQE parameter optimization plus 2.4 minutes (144s) post-optimization sampling/bitstring correction. brock200-1 is a very dense graph (200 nodes, 14834 edges). Best set of size 6 matches QOBLIB's best-known (optimal) value. This submitted run (P=2.0) found 31 distinct maximum-size (6) independent sets: [11,63,107,114,148,170], [5,24,61,118,134,162], [33,37,55,72,96,199], [11,63,107,114,168,170], [10,44,61,73,118,162], [42,43,65,90,146,164], [1,85,121,140,192,200], [33,37,72,96,197,199], [34,52,70,145,151,189], [24,49,96,134,166,176], [24,42,84,91,118,123], [5,30,49,129,134,176], [1,52,117,127,146,152], [2,31,38,66,97,167], [12,69,104,111,141,184], [37,43,72,95,153,169], [33,37,38,81,96,112], [1,19,25,47,131,196], [33,55,64,70,137,190], [5,49,74,129,134,176], [25,63,81,107,133,148], [5,36,55,64,67,161], [25,45,63,81,133,152], [5,7,30,49,134,176], [22,47,81,133,148,181], [84,91,118,123,151,188], [1,33,117,127,146,152], [17,30,34,80,121,140], [1,45,117,122,146,152], [1,12,52,117,146,147], [33,37,55,72,96,112]; a second run with P=4.0 (not separately submitted) found 54 distinct maximum-size sets, with 23 sets overlapping between the two runs. Combined across both runs, 62 distinct maximum-size (6) independent sets have been recovered in total for this instance. |
