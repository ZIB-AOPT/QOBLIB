# Submission for B5_25_1

This directory contains the submission for the problem **B5_25_1**.

| Field | Value 1 |
| --- | --- |
| Problem | B5_25_1 |
| Submitter | George Pennington (1), Naeimeh Mohseni (2) |
| Affiliation | (1) The Hartree Centre STFC, United Kingdom, (2) E.ON Digital Technology GmbH, Essen, Germany |
| Date | August 3rd, 2026 |
| ====== |  |
| Reference | https://arxiv.org/pdf/2509.10657 |
| Best Objective Value | 15 |
| Optimality Bound | N/A |
| ====== |  |
| Modeling Approach | E-FCFW with QAOA sampling and CPLEX weights recomputation. |
| # Decision Variables | 1861 |
| # Binary Variables | 943 |
| # Integer Variables | N/A |
| # Continuous Variables | 918 |
| # Non-Zero Coefficients | 1870 |
| Coefficients Type | Integer |
| Coefficients Range | {0,1,k} (CPLEX) where $k \in {1,2,3,..., n^2}$ is the number of matchings  |
| ====== |  |
| Workflow | Each iteration of E-FCFW calls: 1) QAOA sampling 2) CPLEX weight recomputation |
| Algorithm Type | Stochastic |
| Paradigm | Classical and Quantum |
| # Runs | 1 |
| # Feasible Runs | 1 |
| # Successful Runs | 1 |
| Success Threshold | 1e-6 |
| ====== |  |
| Hardware Specifications | IBM_Boston; MacBook Pro (16-inch, 2021) Apple M1 Max 10-core CPU, 32-core GPU, 64GB RAM |
| ====== |  |
| Total Runtime | 796.25 |
| Time to Solution | N/A |
| CPU Runtime | 0 |
| GPU Runtime | 0 |
| QPU Runtime | 75 |
| Other HW Runtime | 0 |
| ====== |  |
| Remarks | Approximate cost is $f(X) = 1/n^2 \\| X - D^* \\|^2_F$ where $D^*$ is the $n$ by $n$ target doubly stochastic matrix and $X$ its (approximate) decomposition.  |
