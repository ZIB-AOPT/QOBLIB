# Submission for B3_9_5

This directory contains the submission for the problem **B3_9_5**.

| Field | Value 1 |
| --- | --- |
| Problem | B3_9_5 |
| Submitter | Kenji Kanamori |
| Affiliation | Independent Researcher |
| Date | 2026-09-25 |
| ====== |  |
| Reference | README.md in this submission package |
| Best Objective Value | 4 |
| Optimality Bound | 4 |
| ====== |  |
| Modeling Approach | Six-permutation support selection with exact integer-weight reconstruction (dense order-3 instance) |
| # Decision Variables | 6 |
| # Binary Variables | 6 |
| # Integer Variables | 0 |
| # Continuous Variables | 0 |
| # Non-Zero Coefficients | N/A |
| Coefficients Type | Integer |
| Coefficients Range | N/A |
| ====== |  |
| Workflow | Public JSON instance -> Aer role acquisition -> Universal Joint -> fixed Kenji R5 release -> exact weight reconstruction -> official validator |
| Algorithm Type | Stochastic |
| Paradigm | Quantum Simulator |
| # Runs | 5 |
| # Feasible Runs | 5 |
| # Successful Runs | 5 |
| Success Threshold | 0 |
| ====== |  |
| Hardware Specifications | Intel Core Ultra 5 225U CPU; 15.46 GiB RAM; Windows 11; CPU simulation |
| ====== |  |
| Total Runtime | 1.505 |
| Time to Solution | 1.505 |
| CPU Runtime | 1.505 |
| GPU Runtime | N/A |
| QPU Runtime | 0 |
| Other HW Runtime | 0 |
| ====== |  |
| Remarks | Public result statistics and aggregate end-to-end runtimes retained; detailed acquisition and component timing records withdrawn for proprietary-information protection. |

## Instance-specific mathematical optimality

The submitted solution reconstructs the public target matrix using 4 permutation matrices. Exact rational enumeration of every smaller permutation support proves that no feasible decomposition with fewer than 4 matrices exists. Therefore the instance-specific optimum and proven lower bound are both **4**. See the [public certificate](../OPTIMALITY_CERTIFICATE.md) and [reproducible verifier](../verify_optimality.py). This does not certify the proprietary estimator's internal operation or change any recorded run counts.
