# Submission for po_a003_t02_orig

This directory contains the submission for the problem **po_a003_t02_orig**.

| Field | Value 1 |
| --- | --- |
| Problem | po_a003_t02_orig |
| Submitter | Danel Arias [1], Manuel Martín Cordero [1], Daniel García [1], Álvaro Nodar [1] |
| Affiliation | [1] Global Data Quantum, Gran Vía de Don Diego López de Haro, 1, 48001 Bilbo, Bizkaia, Spain |
| Date | 2026-08-05 |
| ====== |  |
| Reference | This submission builds on the ISQR post-processing routine introduced in [I. de León et al., arXiv:2512.22001 (2025)](https://arxiv.org/abs/2512.22001) and applies it to a random sample. ISQR adapts the SQD method to QUBO problems; its extension to the QOBLIB formulation is straightforward. The QUBO follows the model in `06-portfolio/info/model_setting.pdf`, with risk factor λ = 1e-05 and constraint penalty P = 5.0. Full ISQR hyperparameters and the variable mapping are documented in the submission-root README ([../README.md](../README.md)). |
| Best Objective Value | -1595 |
| Optimality Bound | N/A |
| ====== |  |
| Modeling Approach | QUBO (createQUBO_QOBLIB.build_qubo_qoblib): binary vars encode per-period long/short position units, cardinality slack and capital slack |
| # Decision Variables | 20 |
| # Binary Variables | 20 |
| # Integer Variables | 0 |
| # Continuous Variables | 0 |
| # Non-Zero Coefficients | 108 |
| Coefficients Type | Continuous |
| Coefficients Range | -106.667 - 20.0002 |
| ====== |  |
| Workflow | Generate n_shots uniform-random bitstring counts (seeded) -> ISQR post-processing (qoblib_isqr) |
| Algorithm Type | Stochastic |
| Paradigm | Classical |
| # Runs | 10 |
| # Feasible Runs | 10 |
| # Successful Runs | N/A |
| Success Threshold | N/A |
| ====== |  |
| Hardware Specifications | AMD Ryzen 5 PRO 3600 6-Core Processor, 12 logical cores |
| ====== |  |
| Total Runtime | 131 |
| Time to Solution | N/A |
| CPU Runtime | 131 |
| GPU Runtime | N/A |
| QPU Runtime | N/A |
| Other HW Runtime | N/A |
| ====== |  |
| Remarks | Solution file is in the canonical QOBLIB position-line format (`instance`/`budget`/`lambda`/`objective` headers + `period symbol long short` lines), obtained by decoding the raw ISQR bitstring using the variable encoding described in the submission-root README; the bitstring itself is kept as a comment in the `.sol` file. The bitstring selected is the one with the best (lowest) raw QUBO cost among the sampled runs (-204.0878963861868, incl. constraint-penalty term `P=5.0`, not directly comparable to other QOBLIB submissions). |
