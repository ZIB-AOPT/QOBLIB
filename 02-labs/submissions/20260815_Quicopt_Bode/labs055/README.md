# Submission for labs055

This directory contains the submission for the problem **labs055**.

| Field | Value 1 |
| --- | --- |
| Problem | labs055 |
| Submitter | Tim Bode |
| Affiliation | Forschungszentrum Jülich |
| Date | 2026-08-15 |
| ====== |  |
| Reference | https://github.com/Quicopt/Benchmarks |
| Best Objective Value | 171 |
| Optimality Bound | N/A |
| ====== |  |
| Modeling Approach | PUBO |
| # Decision Variables | 55 |
| # Binary Variables | 55 |
| # Integer Variables | 0 |
| # Continuous Variables | 0 |
| # Non-Zero Coefficients | 13482 |
| Coefficients Type | Integer |
| Coefficients Range | 2 - 4 |
| ====== |  |
| Workflow | Build the PUBO from the sequence length, solve with Quicopt v0.2. |
| Algorithm Type | Stochastic |
| Paradigm | Classical |
| # Runs | 5 |
| # Feasible Runs | 5 |
| # Successful Runs | 5 |
| Success Threshold | 0 |
| ====== |  |
| Hardware Specifications | AMD EPYC-Rome, 255 vCPUs, 503 GB RAM; Ubuntu 24.04.4 LTS, Linux 6.8.0, x86-64 |
| ====== |  |
| Total Runtime | 543.840000 |
| Time to Solution | 453.000000 |
| CPU Runtime | 23740.080000 |
| GPU Runtime | 0 |
| QPU Runtime | 0 |
| Other HW Runtime | 0 |
| ====== |  |
| Remarks | Runtimes are averaged over the runs, and are the cost of one answer from cold. Of the average run, 90.8 s wall / 1090.1 s CPU is that run's own work; the remaining 453.0 s wall / 22650.0 s CPU is a stage the runs of this instance have in common, charged to each run in full so that Total Runtime does not fall as runs are added. That stage was in fact executed once for each group of runs that shared it, and the runs were executed concurrently, so the work consumed 28100 s CPU in total rather than # Runs times CPU Runtime. # Successful Runs counts the runs that reached the reported objective (epsilon = 0). |
