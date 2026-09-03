# Submission for brock200-2

This directory contains the submission for the problem **brock200-2**.

| Field | Value 1 |
| --- | --- |
| Problem | brock200-2 |
| Submitter | Kalyan Dasgupta, Sumanta Mukherjee, Dhriti Verma, Surya Shravan Kumar Sajja, Abhishek Singh, Dzung Phan, Jayant Kalagnanam |
| Affiliation | IBM Research - Bangalore - India, IBM Research - Bangalore - India, IBM Research - Yorktown Heights - NY - USA, IBM Research - Bangalore - India, IBM Research - Bangalore - India, IBM Research - Yorktown Heights - NY - USA, IBM Research - Yorktown Heights - NY - USA |
| Date | 2026-08-31 |
| ====== |  |
| Reference | https://arxiv.org/abs/2606.28866 |
| Best Objective Value | 12 |
| Optimality Bound | N/A |
| ====== |  |
| Modeling Approach | Ising Hamiltonian from QUBO relaxation (max sum_i x_i - P*sum_(i,j) in E x_i x_j); spectral (Fiedler) qubit reordering + distance-based sparsification of long-range couplings before circuit construction |
| # Decision Variables | 200 |
| # Binary Variables | 200 |
| # Integer Variables | 0 |
| # Continuous Variables | 0 |
| # Non-Zero Coefficients | 10224 |
| Coefficients Type | Continuous |
| Coefficients Range | J_ij = P/4 (constant over edges); h_i = 0.5 - P*deg_i/4 (varies with node degree); P (penalty) = 4.0 for this run |
| ====== |  |
| Workflow | Build Ising Hamiltonian from graph; spectral reordering; sparsify couplings (max_adj); train EfficientSU2 VQE ansatz (n_reps=2, 1200 parameters) with COBYLA and CVaR (alpha=0.2, initial params = zeros) using AerSimulator (MPS method); post-process samples (100000 shots/trial x 10 trials) with greedy bitstring repair and local-search based bitstring correction to extract maximal independent sets. |
| Algorithm Type | Stochastic |
| Paradigm | Quantum Simulator |
| # Runs | 1 |
| # Feasible Runs | 1 |
| # Successful Runs | 1 |
| Success Threshold | N/A |
| ====== |  |
| Hardware Specifications | MacBook Pro (MacBookPro18,1), Apple M1 Pro, 10 cores (8 performance + 2 efficiency), 32 GB RAM, macOS, using AerSimulator (MPS method). |
| ====== |  |
| Total Runtime | 4019.64 |
| Time to Solution | N/A |
| CPU Runtime | N/A |
| GPU Runtime | N/A |
| QPU Runtime | N/A |
| Other HW Runtime | N/A |
| ====== |  |
| Remarks | TIMING NOTE: we did not measure CPU-process time (e.g. via time.process_time()) or log CPU utilization separately; only wall-clock time (via time.time()) was recorded, so 'CPU Runtime' is left as N/A and the full wall-clock duration is reported under 'Total Runtime' instead. NOTE ON '# Runs': this experiment is a single run (# Runs = 1): one classically-trained VQE circuit (one fixed set of optimized parameters) whose measurement shots were collected across 10 sub-batches (a practical choice for hardware/queue management) and pooled together before classical bitstring correction. The 10 sub-batches are not independent executions of the algorithm, so we do not report them as separate runs. Individual per-batch raw-sample size is not predictive of final MIS quality, since smaller seeds can extend further under maximality-driving (local search); additionally, per our reference paper, the bitstring-correction heuristic uses an EMA that improves cumulatively as more batches are pooled, so later batches benefit from more accumulated signal than earlier ones. '# Feasible Runs' = '# Successful Runs' = 1 reflects that this single pooled campaign produced the reported result, not that 10 independent attempts each succeeded. Total Runtime = 3859.68s classical VQE parameter optimization (AerSimulator MPS) + ~159.96s post-optimization sampling/bitstring correction. Best set of size 12 matches QOBLIB's best-known (optimal) value. Only 1 distinct maximum-size (12) independent set was found among the unique independent sets extracted from 100000 shots/trial x 10 trials of post-optimization sampling (a second set of size 11 was also observed). |
