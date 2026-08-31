# Submission for brock400-1

This directory contains the submission for the problem **brock400-1**.

| Field | Value 1 |
| --- | --- |
| Problem | brock400-1 |
| Submitter | Kalyan Dasgupta, Sumanta Mukherjee, Dhriti Verma, Surya Shravan Kumar Sajja, Abhishek Singh, Dzung Phan, Jayant Kalagnanam |
| Affiliation | IBM Research - Bangalore - India, IBM Research - Bangalore - India, IBM Research - Yorktown Heights - NY - USA, IBM Research - Bangalore - India, IBM Research - Bangalore - India, IBM Research - Yorktown Heights - NY - USA, IBM Research - Yorktown Heights - NY - USA |
| Date | 2026-08-31 |
| ====== |  |
| Reference | https://arxiv.org/abs/2606.28866 |
| Best Objective Value | 25 |
| Optimality Bound | N/A |
| ====== |  |
| Modeling Approach | Ising Hamiltonian from QUBO relaxation (max sum_i x_i - P*sum_(i,j) in E x_i x_j); spectral (Fiedler) qubit reordering + distance-based sparsification of long-range couplings before circuit construction |
| # Decision Variables | 400 |
| # Binary Variables | 400 |
| # Integer Variables | 0 |
| # Continuous Variables | 0 |
| # Non-Zero Coefficients | 20477 |
| Coefficients Type | Continuous |
| Coefficients Range | J_ij = P/4 (constant over edges); h_i = 0.5 - P*deg_i/4 (varies with node degree); P (penalty) = 2.0-6.0 (penalty varied across the iterative warm-start rounds) for this run |
| ====== |  |
| Workflow | Build Ising Hamiltonian from graph; spectral reordering; sparsify couplings (max_adj=4); iteratively train excitation-preserving VQE ansatz (n_reps=2) with SPSA and CVaR, using ancilla qubits to seed a superposition over the best classically-found near-optimal independent sets (warm-start via basis-state seeding) from prior rounds, on AerSimulator (MPS method); post-process samples (100000 shots/trial x 10 trials) with greedy bitstring repair, local-search / iterated local search (ILS) bitstring correction to extract maximal independent sets. |
| Algorithm Type | Stochastic |
| Paradigm | Quantum Simulator |
| # Runs | 10 |
| # Feasible Runs | 10 |
| # Successful Runs | 10 |
| Success Threshold | 0 |
| ====== |  |
| Hardware Specifications | MacBook Pro (MacBookPro18,1), Apple M1 Pro, 10 cores (8 performance + 2 efficiency), 32 GB RAM, macOS, using AerSimulator (MPS method). |
| ====== |  |
| Total Runtime | 14847.07 |
| Time to Solution | N/A |
| CPU Runtime | 14659.54 |
| GPU Runtime | N/A |
| QPU Runtime | N/A |
| Other HW Runtime | N/A |
| ====== |  |
| Remarks | NOTE ON '# Successful Runs': all 10 sampling trials' raw bitstrings are pooled and deduplicated together before the final best independent set is extracted, so no single trial alone reaches the reported best size and it is a joint result of all trials. Individual per-trial raw-sample size is not predictive of final MIS quality, since smaller seeds can extend further under maximality-driving (local search); additionally, per our reference paper, the bitstring-correction heuristic uses an EMA that improves across successive trials, so later trials are more likely to yield the MIS than earlier ones. The trials are not i.i.d. and cannot be scored independently. '# Successful Runs' = 10 reflects that all trials contributed feasible samples to this pooled, cumulative outcome, not that each trial individually matched the best size. Total Runtime = 14659.54s classical VQE parameter optimization (AerSimulator MPS) + 187.53s post-optimization sampling/bitstring correction, for the final confirming round of an iterative ancilla-seeded warm-start procedure spanning ~800+ minutes of cumulative optimization across all rounds (size progression: 0 -> 22 -> 24 -> 25, plateauing at 25 and confirmed by local search / ILS unable to improve further). brock400-1's true optimum is 27; our best recovered independent set has size 25. We report this as a valid feasible heuristic result below QOBLIB's known optimum, per the 'report negative results' guidance in CONTRIBUTING.md. We include the multiplicity: only 1-2 distinct sets of size 25 were found across the later confirming rounds. As discussed in our reference paper, closing this gap to the true optimum (27) at this 400-node scale would require the excitation-preserving ansatz to run with more repetitions, which drives the required MPS bond dimension for classical simulation beyond what is practically tractable on the hardware we have access to. This is a task that only genuine quantum hardware execution, rather than classical MPS simulation, could plausibly fulfil. |
