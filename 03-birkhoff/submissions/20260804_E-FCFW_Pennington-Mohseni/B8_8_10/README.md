# Submission for B8_8_10

This directory contains the submission for the problem **B8_8_10**.

| Field | Value 1 |
| --- | --- |
| Problem | B8_8_10 |
| Submitter | George Pennington (1), Naeimeh Mohseni (2) |
| Affiliation | (1) The Hartree Centre STFC (United Kingdom), (2) E.ON Digital Technology GmbH (Germany) |
| Date | August 4th, 2026 |
| ====== |  |
| Reference | https://arxiv.org/pdf/2509.10657 |
| Best Objective Value | 12 |
| Optimality Bound | N/A |
| ====== |  |
| Modeling Approach | E-FCFW with QAOA sampling and CPLEX weights recomputation. |
| # Decision Variables | 232 |
| # Binary Variables | 148 |
| # Integer Variables | 0 |
| # Continuous Variables | 84 |
| # Non-Zero Coefficients | 168 |
| Coefficients Type | Integer |
| Coefficients Range | {0,1,k} (CPLEX) where $k$ takes values in ${1,2,3,..., n^2}$. |
| ====== |  |
| Workflow | Each iteration of E-FCFW calls: 1) QAOA sampling 2) CPLEX weight recomputation |
| Algorithm Type | Stochastic |
| Paradigm | Quantum Hardware |
| # Runs | 1 |
| # Feasible Runs | 1 |
| # Successful Runs | 0 |
| Success Threshold | 1e-6 |
| ====== |  |
| Hardware Specifications | IBM_Miami; Apple MacBook Pro (2021) M1 Max 32GB RAM |
| ====== |  |
| Total Runtime | 1007 |
| Time to Solution | 1007 |
| CPU Runtime | 461 |
| GPU Runtime | 0 |
| QPU Runtime | 546 |
| Other HW Runtime | 0 |
| ====== |  |
| Remarks | Approximate cost is $f(X) = (1/n^2)  \\| X - D^* \\|^2_F$ where $D^*$ is the $n$ by $n$ target doubly stochastic matrix and $X$ its (approximate) decomposition. The algorithm is executed over $k$ sequential steps, with the number of decision variables increasing at each step. The reported number of decision variables corresponds to the final step, which has the largest number of decision variables. The CPU time is computed using the total usage time in the IBM Quantum platform, minus the QPU time.  |
