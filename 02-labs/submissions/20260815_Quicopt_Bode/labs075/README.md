# Submission for labs075

This directory contains the submission for the problem **labs075**.

| Field | Value 1 |
| --- | --- |
| Problem | labs075 |
| Submitter | Tim Bode |
| Affiliation | Forschungszentrum Jülich |
| Date | 2026-08-15 |
| ====== |  |
| Reference | https://github.com/Quicopt/Benchmarks |
| Best Objective Value | 341 |
| Optimality Bound | N/A |
| ====== |  |
| Modeling Approach | PUBO |
| # Decision Variables | 75 |
| # Binary Variables | 75 |
| # Integer Variables | 0 |
| # Continuous Variables | 0 |
| # Non-Zero Coefficients | 34447 |
| Coefficients Type | Integer |
| Coefficients Range | 2 - 4 |
| ====== |  |
| Workflow | Build the PUBO from the sequence length, solve with Quicopt v0.2. |
| Algorithm Type | Stochastic |
| Paradigm | Classical |
| # Runs | 45 |
| # Feasible Runs | 45 |
| # Successful Runs | 3 |
| Success Threshold | 0 |
| ====== |  |
| Hardware Specifications | AMD EPYC-Rome, 255 vCPUs, 503 GB RAM; Ubuntu 24.04.4 LTS, Linux 6.8.0, x86-64 |
| ====== |  |
| Total Runtime | 944.333333 |
| Time to Solution | 833.557778 |
| CPU Runtime | 32027.551111 |
| GPU Runtime | 0 |
| QPU Runtime | 0 |
| Other HW Runtime | 0 |
| ====== |  |
| Remarks | Runtimes are averaged over the runs, and are the cost of one answer from cold. Of the average run, 447.9 s wall / 2849.8 s CPU is that run's own work; the remaining 496.4 s wall / 29177.8 s CPU is a stage the runs of this instance have in common, charged to each run in full so that Total Runtime does not fall as runs are added. That stage was in fact executed once for each group of runs that shared it, and the runs were executed concurrently, so the work consumed 185040 s CPU in total rather than # Runs times CPU Runtime. # Successful Runs counts the runs that reached the reported objective (epsilon = 0). |
