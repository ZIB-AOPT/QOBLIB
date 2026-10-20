# Submission for B3_3_1

| Field | Value |
| --- | --- |
| Problem | B3_3_1 |
| Submitter | Kenji Kanamori |
| Affiliation | Independent Researcher |
| Date | 2026-10-20 |
| Reference | ../README.md; speed_summary.json; aggregate_results.json |
| Best Objective Value | 2 |
| Optimality Bound | 2 |
| Modeling Approach | Inherited fixed-instance phase-selector preparation; six binary support selections; exact weight reconstruction |
| # Decision Variables | 6 |
| # Binary Variables | 6 |
| # Integer Variables | 0 |
| # Continuous Variables | 0 |
| # Non-Zero Coefficients | N/A |
| Coefficients Type | Integer |
| Coefficients Range | N/A |
| Workflow | Inherited state preparation -> simulator acquisition -> proprietary estimator -> selection decoding -> exact weight reconstruction -> official validation |
| Algorithm Type | Stochastic |
| Paradigm | Quantum Simulator |
| # Runs | 5 |
| # Feasible Runs | 5 |
| # Successful Runs | 5 |
| Success Threshold | 0 |
| Hardware Specifications | Estimator: Intel Core Ultra 5 225U; 12 cores/14 threads; 16602746880 bytes RAM; Windows 11; Python 3.12.10. Linux acquisition host specifications incomplete; see README. |
| Total Runtime | N/A |
| Time to Solution | N/A |
| CPU Runtime | N/A |
| GPU Runtime | 0 |
| QPU Runtime | 0 |
| Other HW Runtime | 0 |
| Remarks | Fixed-instance integration experiment; five independent acquisitions; recorded-input estimator processing. Complete-workflow timing not measured (N/A). Instance-specific optimum of 2 proven from public instance and submitted solution; no new best-known-value record, general unseen-instance solver or comparative speed claim. |

## Optimality certificate

For B3_3_1, a one-permutation decomposition is impossible because the public target matrix has fractional entries (276/1000 and 724/1000). The submitted two-permutation decomposition reconstructs the matrix exactly with nonnegative weights summing to 1. Hence the minimum number of permutation matrices is exactly 2. See [the full instance-specific certificate](../README.md#instance-specific-optimality-certificate-b3_3_1). This is a mathematical certificate for the submitted solution, not a claim about proprietary estimator internals or independent benchmark acceptance.
