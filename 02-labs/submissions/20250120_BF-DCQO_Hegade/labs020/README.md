# Submission for labs020

This directory contains the submission for the problem **labs020**.

| Field | Value 1 |
| --- | --- |
| Problem | labs020 |
| Submitter | Narendra N. Hegade, Alejandro Gomez Cadavid |
| Affiliation | Kipu Quantum, Kipu Quantum and UPV/EHU |
| Date | 2025-01-20 |
| ====== |  |
| Reference | https://github.com/AlejoKQ/data_LABS_BF-DCQO_Benchmark |
| Best Objective Value | 26 |
| Optimality Bound | N/A |
| ====== |  |
| Modeling Approach | HUBO |
| # Decision Variables | 20 |
| # Binary Variables | 20 |
| # Integer Variables | 0 |
| # Continuous Variables | 0 |
| # Non-Zero Coefficients | 615 |
| Coefficients Type | integer |
| Coefficients Range | {2, 4} |
| ====== |  |
| Workflow | Pre-processing: the LABS cost function for N = 20 is mapped to a HUBO with 90 quadratic and 525 quartic terms, and the circuits are built and transpiled with Qiskit. Main algorithm: iterative BF-DCQO, where each iteration samples the digitized counterdiabatic evolution on hardware and updates the bias field from the previous iteration's measurement outcomes. Post-processing: local search sweeps applied to the sampled bitstrings at each iteration. |
| Algorithm Type | Stochastic |
| Paradigm | Quantum Hardware |
| # Runs | 10 |
| # Feasible Runs | 10 |
| # Successful Runs | 10 |
| Success Threshold | 0 |
| ====== |  |
| Hardware Specifications | CPU: Apple M2 Pro; QPU: ibm_marrakesh |
| ====== |  |
| Total Runtime | 61.224 |
| Time to Solution | N/A |
| CPU Runtime | 0.4205 |
| GPU Runtime | N/A |
| QPU Runtime | 60.8 |
| Other HW Runtime | N/A |
| ====== |  |
| Remarks | LABS is unconstrained, so every run is feasible. All runs reached the proven optimum, but Optimality Bound is left as N/A because BF-DCQO derives no bound of its own. Runtimes are averages over the runs. Solutions for each of the 10 runs are in solutions/; see the submission README for the per-run results and software versions. Time is reported in seconds. |
