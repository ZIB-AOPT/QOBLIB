# Submission for labs082

This directory contains the submission for the problem **labs082**.

| Field | Value 1 |
| --- | --- |
| Problem | labs082 |
| Submitter | Tim Bode |
| Affiliation | Forschungszentrum Jülich |
| Date | 2026-08-15 |
| ====== |  |
| Reference | https://github.com/Quicopt/Benchmarks |
| Best Objective Value | 457 |
| Optimality Bound | N/A |
| ====== |  |
| Modeling Approach | PUBO |
| # Decision Variables | 82 |
| # Binary Variables | 82 |
| # Integer Variables | 0 |
| # Continuous Variables | 0 |
| # Non-Zero Coefficients | 45100 |
| Coefficients Type | Integer |
| Coefficients Range | 2 - 4 |
| ====== |  |
| Workflow | Build the PUBO from the sequence length, solve with Quicopt v0.2. |
| Algorithm Type | Stochastic |
| Paradigm | Classical |
| # Runs | 5 |
| # Feasible Runs | 5 |
| # Successful Runs | 1 |
| Success Threshold | 0 |
| ====== |  |
| Hardware Specifications | AMD EPYC-Rome, 255 vCPUs, 503 GB RAM; Ubuntu 24.04.4 LTS, Linux 6.8.0, x86-64 |
| ====== |  |
| Total Runtime | 898.500000 |
| Time to Solution | 867.220000 |
| CPU Runtime | 33164.000000 |
| GPU Runtime | 0 |
| QPU Runtime | 0 |
| Other HW Runtime | 0 |
| ====== |  |
| Remarks | Runtimes are averaged over the runs, and are the cost of one answer from cold. Of the average run, 309.5 s wall / 3714.0 s CPU is that run's own work; the remaining 589.0 s wall / 29450.0 s CPU is a stage the runs of this instance have in common, charged to each run in full so that Total Runtime does not fall as runs are added. That stage was in fact executed once for each group of runs that shared it, and the runs were executed concurrently, so the work consumed 48020 s CPU in total rather than # Runs times CPU Runtime. # Successful Runs counts the runs that reached the reported objective (epsilon = 0). |
