# Submission for labs013

This directory contains the submission for the problem **labs013**.

| Field | Value 1 |
| --- | --- |
| Problem | labs013 |
| Submitter | Kenji Kanamori |
| Affiliation | Independent Researcher |
| Date | 2026-09-13 |
| ====== |  |
| Reference | README.md in this submission package |
| Best Objective Value | 6 |
| Optimality Bound | 6 |
| ====== |  |
| Modeling Approach | Exact elimination of c#1..c#12; 13-qubit canonical phase-path encoding |
| # Decision Variables | 25 |
| # Binary Variables | 13 |
| # Integer Variables | 12 |
| # Continuous Variables | 0 |
| # Non-Zero Coefficients | N/A |
| Coefficients Type | Integer |
| Coefficients Range | N/A |
| ====== |  |
| Workflow | Public LP -> exact elimination -> Aer 5-role sampling -> fixed Kenji release -> decoder -> official validator |
| Algorithm Type | Stochastic |
| Paradigm | Quantum Simulator |
| # Runs | 5 |
| # Feasible Runs | 5 |
| # Successful Runs | 5 |
| Success Threshold | 0 |
| ====== |  |
| Hardware Specifications | Intel Core Ultra 5 225U CPU; 15.46 GiB RAM; Windows 11; CPU simulation |
| ====== |  |
| Total Runtime | 2.131769800 |
| Time to Solution | 2.131769800 |
| CPU Runtime | 2.131769800 |
| GPU Runtime | N/A |
| QPU Runtime | 0 |
| Other HW Runtime | 0 |
| ====== |  |
| Remarks | 5 independent runs (historical run1 plus fresh runs2-5); distinct Aer simulator seed lineages; fixed Kenji RELEASED; official validator PASS for every run; no classical final repair; RUN_QPU=false |

