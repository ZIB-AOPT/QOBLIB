# Submission for labs021

This directory contains the submission for the problem **labs021**.

| Field | Value 1 |
| --- | --- |
| Problem | labs021 |
| Submitter | András Czégel |
| Affiliation | Bentax Plus |
| Date | 2026-11-17 |
| ====== |  |
| Reference | N/A |
| Best Objective Value | 26 |
| Optimality Bound | 26 |
| ====== |  |
| Modeling Approach | Native quartic spin Hamiltonian of LABS (PUBO), no quadratization and no penalty terms. Exact quantum-classical branch and bound (QCBB) with fixed-angle QAOA as the sampler at every node |
| # Decision Variables | 21 |
| # Binary Variables | 21 |
| # Integer Variables | 0 |
| # Continuous Variables | 0 |
| # Non-Zero Coefficients | 715 |
| Coefficients Type | Integer |
| Coefficients Range | 2 - 4 |
| ====== |  |
| Workflow | Best-first branch and bound in one process: at every node the symmetry rule, propagation and the classical lower bound, then sampling of the node Hamiltonian with fixed-angle QAOA (p=12, 1,000 shots, exact noiseless statevector emulation on the CPU, at most 26 qubits; only the root at n = 27-30 is larger and is split into its symmetry classes without being sampled); the samples give incumbents and the branching spin; the run stops when no open node can improve the incumbent |
| Algorithm Type | Stochastic |
| Paradigm | Quantum Simulator |
| # Runs | 5 |
| # Feasible Runs | 5 |
| # Successful Runs | 5 |
| Success Threshold | 0 |
| ====== |  |
| Hardware Specifications | Apple MacBook Pro, M4 Pro (8 performance + 4 efficiency cores), 24 GB RAM |
| ====== |  |
| Total Runtime | 0.3108 |
| Time to Solution | 0.1855 |
| CPU Runtime | 1.0399 |
| GPU Runtime | 0 |
| QPU Runtime | 0 |
| Other HW Runtime | 0 |
| ====== |  |
| Remarks | 5 independent runs with the seeds 1, 2, 3, 4, 5; every run proved optimality, with certified lower bound = energy = 26. A run: one process, fixed-angle QAOA at p=12 on the exact noiseless emulation as the sampler at every node, 1,000 shots per node, no time limit. Best Objective Value: the lowest energy over the runs. Optimality Bound: the largest certified lower bound over the runs; its certificate is labs021_certificate.json. Total Runtime: wall-clock time of the whole solve, from its start to the proof. Time to Solution: wall-clock time from the start until the run first held a sequence of its final energy. CPU Runtime: measured CPU time of all threads of the process. All three are means over the runs. No GPU and no QPU were used; the QAOA circuits are emulated on the CPU. Software: macOS 27.0.1, Python 3.13.7, NumPy 2.5.4, Numba 0.68.1. Model-size columns describe the multilinear expansion of the energy. Energy over the runs: 26, 26, 26, 26, 26. Total runtime [s]: 0.3049, 0.2968, 0.3144, 0.3352, 0.3026; median 0.3049, std 0.0135. Time to solution [s]: 0.1804, 0.1732, 0.1845, 0.2105, 0.1791; median 0.1804, std 0.0130. CPU runtime [s]: 1.0332, 1.0477, 1.0438, 1.0522, 1.0226; median 1.0438, std 0.0107. Nodes evaluated: 381, 381, 381, 381, 381; median 381. |
