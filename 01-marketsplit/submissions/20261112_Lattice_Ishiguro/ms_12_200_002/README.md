# Submission for ms_12_200_002

This directory contains the submission for the problem **ms_12_200_002**.

| Field | Value 1 |
| --- | --- |
| Problem | ms_12_200_002 |
| Submitter | Tsukasa Ishiguro |
| Affiliation | Toyota Motor Corporation |
| Date | 2026-11-12 |
| ====== |  |
| Reference |  |
| Best Objective Value | N/A |
| Optimality Bound | N/A |
| ====== |  |
| Modeling Approach | Lattice |
| # Decision Variables | 110 |
| # Binary Variables | 110 |
| # Integer Variables | 0 |
| # Continuous Variables | 0 |
| # Non-Zero Coefficients | 1315 |
| Coefficients Type | Integer |
| Coefficients Range | 1 - 198 |
| ====== |  |
| Workflow | Lattice embedding (parity-Kannan) -> LLL + BKZ-40 -> G6K GPU sieve (target saturation 0.425) -> scan of the short vectors -> randomized search over combinations of the short vectors (GPU int8 GEMM) -> exact check of Ax=d |
| Algorithm Type | Stochastic |
| Paradigm | Classical |
| # Runs | 5 |
| # Feasible Runs | 5 |
| # Successful Runs | 5 |
| Success Threshold | N/A |
| ====== |  |
| Hardware Specifications | 1x NVIDIA H100 80GB HBM3 (SXM, driver 580.126.20) + 32 threads of 2x Intel Xeon Platinum 8480+ (Supermicro SYS-821GE-TNHR); CUDA 12.4.1, Ubuntu 22.04, Python 3.10.12, fplll 5.4.1, fpylll 0.5.6, PyTorch 2.6.0, CuPy 14.2.0, G6K-GPU-Tensor (branch python3lwe, commit e0e17ad, 2022-01-10) |
| ====== |  |
| Total Runtime | 97.8 |
| Time to Solution | 97.8 |
| CPU Runtime | 97.8 |
| GPU Runtime | 97.8 |
| QPU Runtime | N/A |
| Other HW Runtime | N/A |
| ====== |  |
| Remarks | 5 independent runs (seeds 3-7), all feasible; each run runs the sieve from scratch. Solved by the search over combinations of the short vectors. Runtime = wall clock incl. all stages, mean of 5 runs (min 94 s, max 102 s). Sieve reached target saturation in 5/5 runs. Distinct solutions: solution_0 from seeds 3, 4, 5, 6, 7. CPU (32 threads) and GPU (1) are used concurrently throughout the run; CPU Runtime and GPU Runtime are the same wall-clock time, not busy time. |
