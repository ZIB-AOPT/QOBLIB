# Submission for B6_36_2

This directory contains the submission for the problem **B6_36_2**.

| Field | Value 1 |
| --- | --- |
| Problem | B6_36_2 |
| Submitter | George Pennington (1), Naeimeh Mohseni (2) |
| Affiliation | (1) The Hartree Centre STFC, United Kingdom, (2) E.ON Digital Technology GmbH, Essen, Germany |
| Date | August 3rd, 2026 |
| ====== |  |
| Reference | https://arxiv.org/pdf/2509.10657 |
| Best Objective Value | 19 |
| Optimality Bound | N/A |
| ====== |  |
| Modeling Approach | E-FCFW with QAOA sampling and CPLEX weights recomputation. |
| # Decision Variables | 2808 |
| # Binary Variables | 1422 |
| # Integer Variables | N/A |
| # Continuous Variables | 1386 |
| # Non-Zero Coefficients | 2814 |
| Coefficients Type | Integer |
| Coefficients Range | {0,1,k} (CPLEX) where $k \in {1,2,3,..., n^2}$ is the number of matchings  |
| ====== |  |
| Workflow | Each iteration of E-FCFW calls: 1) QAOA sampling 2) CPLEX weight recomputation |
| Algorithm Type | Stochastic |
| Paradigm | Classical and Quantum |
| # Runs | 1 |
| # Feasible Runs | 1 |
| # Successful Runs | 0 |
| Success Threshold | 1e-6 |
| ====== |  |
| Hardware Specifications | IBM_Pittsburgh; MacBook Pro (16-inch, 2021) Apple M1 Max 10-core CPU, 32-core GPU, 64GB RAM |
| ====== |  |
| Total Runtime | 3346.65 |
| Time to Solution | N/A |
| CPU Runtime | N/A |
| GPU Runtime | 0 |
| QPU Runtime | 95 |
| Other HW Runtime | 0 |
| ====== |  |
| Remarks | Approximate cost is $f(X) = (1/n^2) \\| X - D^* \\|^2_F$ where $D^*$ is the $n$ by $n$ target doubly stochastic matrix and $X$ its (approximate) decomposition.  |
