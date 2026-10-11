# Submission for ITC2021_Middle_11

This directory contains the submission for the problem **ITC2021_Middle_11**.

| Field | Value 1 |
| --- | --- |
| Problem | ITC2021_Middle_11 |
| Submitter | Manan Gupta |
| Affiliation | The Harker School |
| Date | 2026-10-11 |
| ====== |  |
| Reference | https://github.com/mnn31/qoblib-solvers/tree/main/sports |
| Best Objective Value | 0 |
| Optimality Bound | 0 |
| ====== |  |
| Modeling Approach | Constraint programming model of the hard constraints on binary game, home and break indicator variables; no objective. |
| # Decision Variables | 16680 |
| # Binary Variables | 16680 |
| # Integer Variables | 0 |
| # Continuous Variables | 0 |
| # Non-Zero Coefficients | N/A |
| Coefficients Type | N/A |
| Coefficients Range | N/A |
| ====== |  |
| Workflow | Constraint programming. The hard constraints of the instance (round robin structure, phases, CA1 to CA4, GA1, BR1, BR2) are posted directly on binary game variables x[home,away,slot] plus home and break indicators, with no objective. OR-Tools CP-SAT runs its default portfolio of 16 workers until a feasible timetable is found or the time limit expires. Soft constraints are ignored, as the benchmark specifies. Every timetable is verified by an independent checker before being reported. |
| Algorithm Type | Deterministic |
| Paradigm | Classical |
| # Runs | 1 |
| # Feasible Runs | 1 |
| # Successful Runs | 1 |
| Success Threshold | 0 |
| ====== |  |
| Hardware Specifications | RunPod cloud CPU pod on an AMD EPYC 9655 host (96 cores, 192 threads). The container is pinned by cpuset to 16 hardware threads, which are the two SMT siblings of 8 physical cores, with a 64 GB memory limit; Ubuntu 24.04, x86_64, Python 3.12, OR-Tools 9.15. One instance at a time with 16 CP-SAT workers and nothing else running in the container. The host is shared with other tenants, so wall clock times carry some noise. |
| ====== |  |
| Total Runtime | 129.38 |
| Time to Solution | 129.38 |
| CPU Runtime | 129.38 |
| GPU Runtime | N/A |
| QPU Runtime | N/A |
| Other HW Runtime | N/A |
| ====== |  |
| Remarks | No feasible solution was on record for this instance before this submission. Pure feasibility problem: the objective is 0 for any timetable that satisfies all hard constraints, so 0 is also the bound. 20 teams, 38 slots, phased, 176 hard constraints. Single run with fixed CP-SAT seed 0; the 16 worker portfolio search is not bitwise reproducible, so repeated runs can differ in time. Time limit 600 s; runtime is wall clock including model build. Verified with an independent checker and with the official RobinX validator (infeasibility 0, soft penalty 4228, not part of the benchmark objective); a RobinX XML copy is included. |
