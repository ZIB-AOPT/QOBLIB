# Submission for labs099

This directory contains the submission for the problem **labs099**.

| Field | Value 1 |
| --- | --- |
| Problem | labs099 |
| Submitter | Tim Bode |
| Affiliation | Forschungszentrum Jülich |
| Date | 2026-08-15 |
| ====== |  |
| Reference | https://github.com/Quicopt/Benchmarks |
| Best Objective Value | 725 |
| Optimality Bound | N/A |
| ====== |  |
| Modeling Approach | PUBO |
| # Decision Variables | 99 |
| # Binary Variables | 99 |
| # Integer Variables | 0 |
| # Continuous Variables | 0 |
| # Non-Zero Coefficients | 79625 |
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
| Total Runtime | 975.380000 |
| Time to Solution | 876.100000 |
| CPU Runtime | 29298.560000 |
| GPU Runtime | 0 |
| QPU Runtime | 0 |
| Other HW Runtime | 0 |
| ====== |  |
| Remarks | A run has two parts. Work done for that run alone takes 512 s wall and 6149 s CPU on average. A preparation step, shared by all 5 runs of this instance, takes 463 s wall and 23150 s CPU. The runtimes above charge that shared step to every run, so they say what one sequence costs from a cold start, and they do not shrink as more runs are added. All 5 runs together actually used 53893 s CPU. That is less than 5 times CPU Runtime, because the shared step ran once rather than 5 times and the runs ran side by side. Successful runs are those that reached the reported objective exactly. |
