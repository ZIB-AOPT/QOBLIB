# Submission for po_a005_t04_orig

This directory contains the submission for the problem **po_a005_t04_orig**.

| Field | Value 1 |
| --- | --- |
| Problem | po_a005_t04_orig |
| Submitter | Danel Arias [1], Manuel Martín Cordero [1], Daniel García [1], Álvaro Nodar [1] |
| Affiliation | [1] Global Data Quantum, Gran Vía de Don Diego López de Haro, 1, 48001 Bilbo, Bizkaia, Spain |
| Date | 2026-08-05 |
| ====== |  |
| Reference | This submission builds on the ISQR post-processing routine introduced in [I. de León et al., arXiv:2512.22001 (2025)](https://arxiv.org/abs/2512.22001) and applies it to a random sample. ISQR adapts the SQD method to QUBO problems; its extension to the QOBLIB formulation is straightforward. The QUBO follows the model in `06-portfolio/info/model_setting.pdf`, with risk factor λ = 4e-05 and constraint penalty P = 0.5. Full ISQR hyperparameters and the variable mapping are documented in the submission-root README ([../README.md](../README.md)). |
| Best Objective Value | N/A |
| Optimality Bound | N/A |
| ====== |  |
| Modeling Approach | QUBO (createQUBO_QOBLIB.build_qubo_qoblib): binary vars encode per-period long/short position units, cardinality slack and capital slack |
| # Decision Variables | 148 |
| # Binary Variables | 148 |
| # Integer Variables | 0 |
| # Continuous Variables | 0 |
| # Non-Zero Coefficients | 2854 |
| Coefficients Type | Continuous |
| Coefficients Range | -128 - 32 |
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
| Remarks | |
