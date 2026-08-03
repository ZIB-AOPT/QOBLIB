# Submission for B32_1024_6

This directory contains the submission for the problem **B32_1024_6**.

| Field | Value 1 |
| --- | --- |
| Problem | B32_1024_6 |
| Submitter | Víctor Valls |
| Affiliation | IBM Research Europe — Dublin |
| Date | August 3rd, 2026 |
| ====== |  |
| Reference | 10.1109/TNET.2021.3088327 |
| Best Objective Value | 205 |
| Optimality Bound | N/A |
| ====== |  |
| Modeling Approach | Birkhoff algorithm with max-weight-type matchings. |
| # Decision Variables | 1025 |
| # Binary Variables | 1024 |
| # Integer Variables | 1 |
| # Continuous Variables | 0 |
| # Non-Zero Coefficients | 64 |
| Coefficients Type | Binary |
| Coefficients Range | 1 |
| ====== |  |
| Workflow | Algorithm runs in steps. Each step computes a matching and a weight. |
| Algorithm Type | Deterministic |
| Paradigm | Classical |
| # Runs | 1 |
| # Feasible Runs | 1 |
| # Successful Runs | 1 |
| Success Threshold | 0 |
| ====== |  |
| Hardware Specifications | MacBook Pro (16-inch, 2021) Apple M1 Max 10-core CPU, 32-core GPU, 64GB RAM |
| ====== |  |
| Total Runtime | 0.464 |
| Time to Solution | 0.464 |
| CPU Runtime | 0.464 |
| GPU Runtime | 0 |
| QPU Runtime | 0 |
| Other HW Runtime | 0 |
| ====== |  |
| Remarks | The number of non-zero coefficient is equal to the number of constraints (each row and column must sum to 1). |
