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
| # Runs | 5 |
| # Feasible Runs | 5 |
| # Successful Runs | 5 |
| Success Threshold | N/A |
| ====== |  |
| Hardware Specifications | MacBook Pro, Apple M1 Pro, 10 cores (8 performance + 2 efficiency), 32 GB RAM, macOS, using AerSimulator (MPS method). |
| ====== |  |
| Total Runtime | 14847.07 |
| Time to Solution | N/A |
| CPU Runtime | N/A |
| GPU Runtime | N/A |
| QPU Runtime | N/A |
| Other HW Runtime | N/A |
| ====== |  |
| Remarks | TIMING NOTE: we did not measure CPU-process time (e.g. via time.process_time()) or log CPU utilization separately; only wall-clock time (via time.time()) was recorded, so 'CPU Runtime' is left as N/A and the full wall-clock duration is reported under 'Total Runtime' instead. NOTE ON '# Runs': we report 5 runs (# Runs = 5), one per distinct VQE training round of the iterative ancilla-seeded warm-start procedure (each round retrains the circuit, seeded from the previous round's best solutions, then runs its own pooled sampling-and-correction campaign spanning 10 measurement-shot sub-batches as described above). All 5 rounds reached size 25. '# Feasible Runs' = '# Successful Runs' = 5. Total Runtime = 14659.54s classical VQE parameter optimization (AerSimulator MPS) + 187.53s post-optimization sampling/bitstring correction, for the final confirming round of an iterative ancilla-seeded warm-start procedure spanning ~800+ minutes of cumulative optimization across all rounds (size progression: 0 -> 22 -> 24 -> 25, plateauing at 25 and confirmed by local search / ILS unable to improve further). brock400-1's true optimum is 27; our best recovered independent set has size 25. We report this as a valid feasible heuristic result below QOBLIB's known optimum, per the 'report negative results' guidance in CONTRIBUTING.md. We include the multiplicity: across all confirming rounds of the iterative warm-start procedure, 12 distinct sets of size 25 were found in total (not just the 1-2 from the final round alone); all 12 are provided as separate, independently verified files in the solutions/ directory. As discussed in our reference paper, closing this gap to the true optimum (27) at this 400-node scale would require the excitation-preserving ansatz to run with more repetitions, which drives the required MPS bond dimension for classical simulation beyond what is practically tractable on the hardware we have access to. This is a task that only quantum hardware execution, rather than classical MPS simulation, could plausibly fulfil. |
