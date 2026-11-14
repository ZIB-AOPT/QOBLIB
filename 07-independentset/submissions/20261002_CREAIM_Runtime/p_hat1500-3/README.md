# Submission for p_hat1500-3

This directory contains the submission for the problem **p_hat1500-3**.

| Field | Value 1 |
| --- | --- |
| Problem | p_hat1500-3 |
| Submitter | CREAIM Research Team |
| Affiliation | CREAIM Inc. |
| Date | 2026-10-02 |
| Reference | https://github.com/hsm6954-boop/CREAIM-Runtime-QOBLIB-Reproducibility |
| Best Objective Value | 94 |
| Optimality Bound | N/A |
| Modeling Approach | Direct binary maximum-independent-set formulation: maximize sum(x_v), subject to x_u + x_v <= 1 for every graph edge. |
| # Decision Variables | 1500 |
| # Binary Variables | 1500 |
| # Integer Variables | 0 |
| # Continuous Variables | 0 |
| # Non-Zero Coefficients | 555512 |
| Coefficients Type | Integer/binary linear coefficients |
| Coefficients Range | 1 to 1 |
| Workflow | Parse the public instance; execute the proprietary CREAIM Runtime classical stochastic solver under the fixed submitted run protocol; independently recheck stable-set feasibility; retain the best feasible solution. |
| Algorithm Type | Stochastic |
| Paradigm | Classical |
| # Runs | 10 |
| # Feasible Runs | 10 |
| # Successful Runs | 9 |
| Success Threshold | 0 |
| Hardware Specifications | Base44 sandbox; 4 vCPU x86_64 virtualized AuthenticAMD family 25 model 17; Linux/gVisor; GCC 12.2.0; OMP_NUM_THREADS=4; no GPU; no QPU |
| Total Runtime | 0.977763 |
| Time to Solution | N/A |
| CPU Runtime | N/A |
| GPU Runtime | 0 |
| QPU Runtime | 0 |
| Other HW Runtime | 0 |
| Remarks | Reference-blind classical run. QOBLIB ledger status at frozen source: optimal. CREAIM does not claim an independent optimality proof. Fixed outer seed base 28123 and stride 100003; OMP_NUM_THREADS=4. Solver build SHA-256 85bd754b14aa1679df290d2b5c68658ddfe225d1cb5209d85247c76bf027b76a. Solution SHA-256 3d1183137106fc08c374aa78248f27d443ec995e5339aa9321d0a2a7e6d6ed20. |
