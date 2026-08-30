# Submission for labs015

This directory contains the submission for the problem **labs015**.

| Field | Value 1 |
| --- | --- |
| Problem | labs015 |
| Submitter | Qin.Z |
| Affiliation | N/A |
| Date | 2026-08-22 |
| ====== |  |
| Reference | https://github.com/QoriZii/quantum-optim |
| Best Objective Value | 15 |
| Optimality Bound | N/A |
| ====== |  |
| Modeling Approach | HUBO |
| # Decision Variables | 15 |
| # Binary Variables | 15 |
| # Integer Variables | 0 |
| # Continuous Variables | 0 |
| # Non-Zero Coefficients | 252 |
| Coefficients Type | Integer |
| Coefficients Range | {1, 2} |
| ====== |  |
| Workflow | LABS cost function mapped to a HUBO as Pauli Z-strings; QAOA with a scipy classical optimizer (default BFGS) on a local Aer statevector simulator; best sampled bitstring per run. |
| Algorithm Type | Stochastic |
| Paradigm | Quantum Simulator |
| # Runs | 5 |
| # Feasible Runs | 5 |
| # Successful Runs | 5 |
| Success Threshold | 0 |
| ====== |  |
| Hardware Specifications | Intel(R) Xeon(R) CPU @ 2.20GHz \| Linux-6.6.122+-x86_64-with-glibc2.35 \| 13 GB \| GPU: N/A |
| ====== |  |
| Total Runtime | 1.349 |
| Time to Solution | 0.918 |
| CPU Runtime | 1.349 |
| GPU Runtime | N/A |
| QPU Runtime | N/A |
| Other HW Runtime | N/A |
| ====== |  |
| Remarks | QAOA p=1, 2048 shots/eval, BFGS maxiter=200, seeds=[0, 1, 2, 3, 4]. Runtimes are averages over the 5 runs. |
