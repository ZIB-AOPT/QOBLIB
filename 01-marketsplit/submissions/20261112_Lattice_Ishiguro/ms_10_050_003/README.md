# Submission for ms_10_050_003

This directory contains the submission for the problem **ms_10_050_003**.

| Field | Value 1 |
| --- | --- |
| Problem | ms_10_050_003 |
| Submitter | Tsukasa Ishiguro |
| Affiliation | Toyota Motor Corporation |
| Date | 2026-11-12 |
| ====== |  |
| Reference |  |
| Best Objective Value | 0.0 |
| Optimality Bound | N/A |
| ====== |  |
| Modeling Approach | Lattice |
| # Decision Variables | 90 |
| # Binary Variables | 90 |
| # Integer Variables | 0 |
| # Continuous Variables | 0 |
| # Non-Zero Coefficients | 880 |
| Coefficients Type | Integer |
| Coefficients Range | 1 - 48 |
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
| Total Runtime | 13.4 |
| Time to Solution | 13.4 |
| CPU Runtime | 13.4 |
| GPU Runtime | 13.4 |
| QPU Runtime | N/A |
| Other HW Runtime | N/A |
| ====== |  |
| Remarks | 5 independent runs (seeds 3-7), all feasible; each run runs the sieve from scratch. Solved by the scan of the short vectors or the search over their combinations, depending on the run. Runtime = wall clock incl. all stages, mean of 5 runs; the individual runs (seeds 3, 4, 5, 6, 7) took 14 / 13 / 16 / 12 / 12 s. Sieve reached target saturation in 5/5 runs. Distinct solutions: solution_0 from seed 3; solution_1 from seed 4; solution_2 from seed 5; solution_3 from seed 6; solution_4 from seed 7. CPU (32 threads) and GPU (1) are reserved exclusively for the whole run and are used concurrently during the sieve; they do not run simultaneously for the entire run (the LLL/BKZ basis reduction does not use the GPU, which is negligible in the total wall clock, and the CPU also waits on the GPU at times). CPU Runtime and GPU Runtime are therefore the same wall-clock time, not busy time. |
