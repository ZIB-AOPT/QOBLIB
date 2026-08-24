# Submission for labs072

This directory contains the submission for the problem **labs072**.

| Field | Value 1 |
| --- | --- |
| Problem | labs072 |
| Submitter | Tim Bode |
| Affiliation | Forschungszentrum Jülich |
| Date | 2026-08-15 |
| ====== |  |
| Reference | https://github.com/Quicopt/Benchmarks |
| Best Objective Value | 300 |
| Optimality Bound | N/A |
| ====== |  |
| Modeling Approach | PUBO |
| # Decision Variables | 72 |
| # Binary Variables | 72 |
| # Integer Variables | 0 |
| # Continuous Variables | 0 |
| # Non-Zero Coefficients | 30450 |
| Coefficients Type | Integer |
| Coefficients Range | 2 - 4 |
| ====== |  |
| Workflow | Build the PUBO from the sequence length, solve with Quicopt v0.2. |
| Algorithm Type | Stochastic |
| Paradigm | Classical |
| # Runs | 40 |
| # Feasible Runs | 40 |
| # Successful Runs | 1 |
| Success Threshold | 0 |
| ====== |  |
| Hardware Specifications | AMD EPYC-Rome, 255 vCPUs, 503 GB RAM; Ubuntu 24.04.4 LTS, Linux 6.8.0, x86-64 |
| ====== |  |
| Total Runtime | 707.307500 |
| Time to Solution | 554.507500 |
| CPU Runtime | 21739.845000 |
| GPU Runtime | 0 |
| QPU Runtime | 0 |
| Other HW Runtime | 0 |
| ====== |  |
| Remarks | A run has two parts. Work done for that run alone takes 383 s wall and 2300 s CPU on average. A preparation step, shared by all 40 runs of this instance, takes 324 s wall and 19440 s CPU. The runtimes above charge that shared step to every run, so they say what one sequence costs from a cold start, and they do not shrink as more runs are added. All 40 runs together actually used 111434 s CPU. That is less than 40 times CPU Runtime, because the shared step ran once rather than 40 times and the runs ran side by side. Successful runs are those that reached the reported objective exactly. |
