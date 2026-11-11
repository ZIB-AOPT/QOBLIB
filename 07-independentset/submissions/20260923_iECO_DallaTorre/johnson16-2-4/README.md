# Submission for johnson16-2-4

This directory contains the submission for the problem **johnson16-2-4**.

| Field | Value 1 |
| --- | --- |
| Problem | johnson16-2-4 |
| Submitter | Emanuele Dalla Torre |
| Affiliation | QuantyMize Quantum Advance Ltd |
| Date | 2026-09-23 |
| ====== |  |
| Reference | https://github.com/ZIB-AOPT/QOBLIB/pull/78 |
| Best Objective Value | 15 |
| Optimality Bound | N/A |
| ====== |  |
| Modeling Approach | MIS QUBO: minimize -sum_v x_v + 2 sum_(u,v in E) x_u x_v |
| # Decision Variables | 120 |
| # Binary Variables | 120 |
| # Integer Variables | 0 |
| # Continuous Variables | 0 |
| # Non-Zero Coefficients | 5580 |
| Coefficients Type | integer |
| Coefficients Range | -1 to 2 |
| ====== |  |
| Workflow | One proprietary iECO optimization step with topology-aware routing and 2024 QPU shots. Classical post-processing decodes each measured candidate to the full graph, with unmapped vertices set to 0. Candidates are prioritized by penalized MIS energy, conflict count, selected-vertex count, and observed frequency. Repair repeatedly removes the selected vertex with the most currently selected neighbors; ties prefer larger graph degree and then lower vertex index. Expansion visits excluded vertices in increasing degree and index order and adds a vertex if it has no selected neighbor. Candidate repairs may run in parallel and stop when the target objective is reached; otherwise the best feasible repaired candidate is retained. Feasibility is verified against all graph edges. |
| Algorithm Type | Stochastic |
| Paradigm | Quantum Hardware |
| # Runs | 5 |
| # Feasible Runs | 5 |
| # Successful Runs | 5 |
| Success Threshold | 0.0 |
| ====== |  |
| Hardware Specifications | IBM Quantum ibm_kingston QPU; classical pre-processing and post-processing on Intel Core Ultra 7 155U; Python 3.14.4; Qiskit 2.4.0; qiskit-ibm-runtime 0.46.1; NumPy 2.4.4 |
| ====== |  |
| Total Runtime | 3.9810 |
| Time to Solution | N/A |
| CPU Runtime | 1.4228 |
| GPU Runtime | 0.0 |
| QPU Runtime | 2.5582 |
| Other HW Runtime | 0.0 |
| ====== |  |
| Remarks | Average seconds over 5 runs; queue time excluded. CPU Runtime covers the instance-specific workflow: generic topology-aware preprocessing, circuit construction, greedy conflict repair, maximal independent-set expansion, and selection of the best feasible result obtained. A generic mapping of the QPU topology is pre-established as part of the protocol; its one-time preparation is excluded. Circuit compilation, provider communication, and queue time are excluded. QPU Runtime is the IBM Sampler execution-span window. One iECO step and 2024 shots per run; optimization level 0; no twirling or dynamical decoupling. Classical repair is part of the reported workflow. iECO's internal optimization construction is proprietary and is not publicly disclosed. The repair is a separate conventional greedy heuristic, fully described in Workflow; no separate publication is cited for this implementation. No raw QPU samples or provider payloads are included. |
