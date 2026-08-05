# Submission for B6_36_4

This directory contains the submission for the problem **B6_36_4**.

| Field | Value 1 |
| --- | --- |
| Problem | B6_36_4 |
| Submitter | George Pennington (1), Naeimeh Mohseni (2) |
| Affiliation | (1) The Hartree Centre STFC, United Kingdom, (2) E.ON Digital Technology GmbH, Essen, Germany |
| Date | August 4th, 2026 |
| ====== |  |
| Reference | https://arxiv.org/pdf/2509.10657 |
| Best Objective Value | 18 |
| Optimality Bound | N/A |
| ====== |  |
| Modeling Approach | E-FCFW with QAOA sampling and CPLEX weights recomputation. |
| # Decision Variables | 276 |
| # Binary Variables | 156 |
| # Integer Variables | N/A |
| # Continuous Variables | 120 |
| # Non-Zero Coefficients | 240 |
| Coefficients Type | Integer |
| Coefficients Range | {0,1,k} (CPLEX) where $k$ takes values in ${1,2,3,..., n^2}$. |
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
| Total Runtime | 3314.23 |
| Time to Solution | 656 |
| CPU Runtime | 561 |
| GPU Runtime | N/A |
| QPU Runtime | 95 |
| Other HW Runtime | N/A |
| ====== |  |
| Remarks | Approximate cost is $f(X) = (1/n^2)  \\| X - D^* \\|^2_F$ where $D^*$ is the $n$ by $n$ target doubly stochastic matrix and $X$ its (approximate) decomposition. The algorithm is executed over $k$ sequential steps, with the number of decision variables increasing at each step. The reported number of decision variables corresponds to the final step, which has the largest number of decision variables. The CPU time is computed using the total usage time in the IBM Quantum platform, minus the QPU time.  |
