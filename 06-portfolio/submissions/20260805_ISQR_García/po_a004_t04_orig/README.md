# Submission for po_a004_t04_orig

This directory contains the submission for the problem **po_a004_t04_orig**.

| Field | Value 1 |
| --- | --- |
| Problem | po_a004_t04_orig |
| Submitter | Danel Arias<sup>1</sup>, Manuel Martín Cordero<sup>1</sup>, Daniel García<sup>1</sup>, Álvaro Nodar<sup>1</sup> |
| Affiliation | <sup>1</sup>Global Data Quantum, Gran Vía de Don Diego López de Haro, 1, 48001 Bilbo, Bizkaia, Spain |
| Date | 2026-08-05 |
| ====== |  |
| Reference | This submission builds on the ISQR post-processing routine introduced in [[I. de León et al., arXiv:2512.22001 (2025)](https://arxiv.org/abs/2512.22001)] and applies it to a random sample. ISQR adapts the SQD method to QUBO problems, and its extension to the QOBLIB formulation is straightforward. The table below summarizes the hyperparameter values selected to ensure convergence. <br><br>**ISQR Hyperparameters:**<br><table><tr><th>Hyperparameter</th><th>Value</th><th>Description</th></tr><tr><td>n_shots</td><td>25000</td><td>Uniform-random bitstrings sampled per seed before ISQR post-processing</td></tr><tr><td>isqr_n_batches (M)</td><td>100</td><td>Number of batches the sampled bitstrings are split into</td></tr><tr><td>isqr_samples_per_batch (Nb)</td><td>1000</td><td>Bitstrings per batch (n_shots = M x Nb)</td></tr><tr><td>isqr_iterations</td><td>10</td><td>Maximum number of Configuration Recovery (CR) refinement iterations</td></tr><tr><td>isqr_tol</td><td>0.05</td><td>Convergence threshold: CR stops early if the relative change in optimization cost between consecutive iterations falls below this value</td></tr><tr><td>isqr_eps</td><td>0.01</td><td>Filling-factor / leaky-ReLU threshold parameter of the CR bit-flip probability function</td></tr></table> |
| Best Objective Value | N/A |
| Optimality Bound | N/A |
| ====== |  |
| Modeling Approach | QUBO (createQUBO_QOBLIB.build_qubo_qoblib): binary vars encode per-period long/short position units, cardinality slack and capital slack |
| # Decision Variables | 120 |
| # Binary Variables | 120 |
| # Integer Variables | 0 |
| # Continuous Variables | 0 |
| # Non-Zero Coefficients | 1896 |
| Coefficients Type | Continuous |
| Coefficients Range | -97.1429 - 16 |
| ====== |  |
| Workflow | Generate n_shots uniform-random bitstring counts (seeded) -> ISQR post-processing (qoblib_isqr) |
| Algorithm Type | Stochastic |
| Paradigm | Classical |
| # Runs | 10 |
| # Feasible Runs | 0 |
| # Successful Runs | N/A |
| Success Threshold | N/A |
| ====== |  |
| Hardware Specifications | AMD Ryzen 5 PRO 3600 6-Core Processor, 12 logical cores |
| ====== |  |
| Total Runtime | N/A |
| Time to Solution | N/A |
| CPU Runtime | N/A |
| GPU Runtime | N/A |
| QPU Runtime | N/A |
| Other HW Runtime | N/A |
| ====== |  |
| Remarks |  |
