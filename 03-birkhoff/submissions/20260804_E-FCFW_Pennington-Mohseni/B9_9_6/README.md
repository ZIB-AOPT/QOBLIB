# Submission for B9_9_6

This directory contains the submission for the problem **B9_9_6**.

| Field | Value 1 |
| --- | --- |
| Problem | B9_9_6 |
| Submitter | George Pennington (1), Naeimeh Mohseni (2) |
| Affiliation | (1) The Hartree Centre STFC, United Kingdom, (2) E.ON Digital Technology GmbH, Essen, Germany |
| Date | August 4th, 2026 |
| ====== |  |
| Reference | https://arxiv.org/pdf/2509.10657 |
| Best Objective Value | 23 |
| Optimality Bound | N/A |
| ====== |  |
| Modeling Approach | E-FCFW with QAOA sampling and CPLEX weights recomputation. |
| # Decision Variables | 369 |
| # Binary Variables | 225 |
| # Integer Variables | 0 |
| # Continuous Variables | 144 |
| # Non-Zero Coefficients | 288 |
| Coefficients Type | Integer |
| Coefficients Range | {0,1,k} (CPLEX) where $k$ takes values in ${1,2,3,..., n^2}$. |
| ====== |  |
| Workflow | Each iteration of E-FCFW calls: 1) QAOA sampling 2) CPLEX weight recomputation |
| Algorithm Type | Stochastic |
| Paradigm | Classical and Quantum |
| # Runs | 1 |
| # Feasible Runs | 1 |
| # Successful Runs | 1 |
| Success Threshold | 1e-6 |
| ====== |  |
| Hardware Specifications | IBM_Kingston; Apple MacBook Pro (2021) M1 Max 32GB RAM |
| ====== |  |
| Total Runtime | 1061 |
| Time to Solution | 1061 |
| CPU Runtime | 946 |
| GPU Runtime | 0 |
| QPU Runtime | 115 |
| Other HW Runtime | 0 |
| ====== |  |
| Remarks | Approximate cost is $f(X) = (1/n^2)  \\| X - D^* \\|^2_F$ where $D^*$ is the $n$ by $n$ target doubly stochastic matrix and $X$ its (approximate) decomposition. The algorithm is executed over $k$ sequential steps, with the number of decision variables increasing at each step. The reported number of decision variables corresponds to the final step, which has the largest number of decision variables. The CPU time is computed using the total usage time in the IBM Quantum platform, minus the QPU time.  |
