# Submission for labs017

This directory contains the submission for the problem **labs017**.

| Field | Value 1 |
| --- | --- |
| Problem | labs017 |
| Submitter | András Czégel |
| Affiliation | Bentax Plus |
| Date | 2026-11-17 |
| ====== |  |
| Reference | N/A |
| Best Objective Value | 32 |
| Optimality Bound | 32 |
| ====== |  |
| Modeling Approach | Native quartic spin Hamiltonian of LABS (PUBO), no quadratization and no penalty terms. Exact quantum-classical branch and bound (QCBB) with fixed-angle QAOA as the sampler at every node |
| # Decision Variables | 17 |
| # Binary Variables | 17 |
| # Integer Variables | 0 |
| # Continuous Variables | 0 |
| # Non-Zero Coefficients | 372 |
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
| Total Runtime | 0.0694 |
| Time to Solution | 0.0603 |
| CPU Runtime | 0.1639 |
| GPU Runtime | 0 |
| QPU Runtime | 0 |
| Other HW Runtime | 0 |
| ====== |  |
| Remarks | 5 independent runs with the seeds 1, 2, 3, 4, 5; every run proved optimality, with certified lower bound = energy = 32. A run: one process, fixed-angle QAOA at p=12 on the exact noiseless emulation as the sampler at every node, 1,000 shots per node, no time limit. Best Objective Value: the lowest energy over the runs. Optimality Bound: the largest certified lower bound over the runs; its certificate is labs017_certificate.json. Total Runtime: wall-clock time of the whole solve, from its start to the proof. Time to Solution: wall-clock time from the start until the run first held a sequence of its final energy. CPU Runtime: measured CPU time of all threads of the process. All three are means over the runs. No GPU and no QPU were used; the QAOA circuits are emulated on the CPU. Software: macOS 27.0.1, Python 3.13.7, NumPy 2.5.4, Numba 0.68.1. Model-size columns describe the multilinear expansion of the energy. Energy over the runs: 32, 32, 32, 32, 32. Total runtime [s]: 0.0707, 0.0693, 0.0697, 0.0689, 0.0685; median 0.0693, std 0.0008. Time to solution [s]: 0.0582, 0.0612, 0.0611, 0.0608, 0.0604; median 0.0608, std 0.0011. CPU runtime [s]: 0.1575, 0.1680, 0.1633, 0.1663, 0.1644; median 0.1644, std 0.0036. Nodes evaluated: 319, 319, 319, 319, 319; median 319. |
