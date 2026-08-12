# Submission for B7_7_2

This directory contains the submission for the problem **B7_7_2**.

| Field | Value 1 |
| --- | --- |
| Problem | B7_7_2 |
| Submitter | George Pennington (1), Naeimeh Mohseni (2) |
| Affiliation | (1) The Hartree Centre STFC (United Kingdom), (2) E.ON Digital Technology GmbH (Germany) |
| Date | August 4th, 2026 |
| ====== |  |
| Reference | https://arxiv.org/pdf/2509.10657 |
| Best Objective Value | 15 |
| Optimality Bound | N/A |
| ====== |  |
| Modeling Approach | E-FCFW with QAOA sampling and CPLEX weights recomputation. |
| # Decision Variables | 241 |
| # Binary Variables | 145 |
| # Integer Variables | 0 |
| # Continuous Variables | 96 |
| # Non-Zero Coefficients | 192 |
| Coefficients Type | Integer |
| Coefficients Range | {0,1,k} (CPLEX) where $k$ takes values in ${1,2,3,..., n^2}$. |
| ====== |  |
| Workflow | Each iteration of E-FCFW calls: 1) QAOA sampling 2) CPLEX weight recomputation |
| Algorithm Type | Stochastic |
| Paradigm | Quantum Hardware |
| # Runs | 1 |
| # Feasible Runs | 1 |
| # Successful Runs | 1 |
| Success Threshold | 1e-6 |
| ====== |  |
| Hardware Specifications | IBM_Pittsburgh; Apple MacBook Pro (2021) M1 Max 32GB RAM |
| ====== |  |
| Total Runtime | 424 |
| Time to Solution | 424 |
| CPU Runtime | 349 |
| GPU Runtime | 0 |
| QPU Runtime | 75 |
| Other HW Runtime | 0 |
| ====== |  |
| Remarks | Approximate cost is $f(X) = (1/2) (1/n^2) \\| X - D^* \\|^2_F$ where $D^*$ is the $n$ by $n$ target doubly stochastic matrix and $X$ its (approximate) decomposition. The approximate decomposition is $X = sum_i \lambda[i] permutation[i]$ where lambda[i] = w[i] / sum_j w[j] is a normalized weight. The cost reported in the 'objective_time_series' does not use normalized weights except in the last entry. <br>The algorithm is executed over $k$ sequential steps, with the number of decision variables increasing at each step. The reported number of decision variables corresponds to the final step, which has the largest number of decision variables. The CPU time is computed using the total usage time in the IBM Quantum platform, minus the QPU time.  |
