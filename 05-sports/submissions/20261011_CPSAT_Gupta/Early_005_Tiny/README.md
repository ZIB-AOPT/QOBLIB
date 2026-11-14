# Submission for Early_005_Tiny

This directory contains the submission for the problem **Early_005_Tiny**.

| Field | Value 1 |
| --- | --- |
| Problem | Early_005_Tiny |
| Submitter | Manan Gupta |
| Affiliation | The Harker School |
| Date | 2026-11-14 |
| ====== |  |
| Reference | https://github.com/mnn31/qoblib-solvers/tree/c83703b5de3b9c998407b3f4375b7034f7394382/sports |
| Best Objective Value | 0 |
| Optimality Bound | 0 |
| ====== |  |
| Modeling Approach | Constraint programming model of the hard constraints on binary game, home and break indicator variables; no objective. |
| # Decision Variables | 468 |
| # Binary Variables | 468 |
| # Integer Variables | 0 |
| # Continuous Variables | 0 |
| # Non-Zero Coefficients | N/A |
| Coefficients Type | N/A |
| Coefficients Range | N/A |
| ====== |  |
| Workflow | Constraint programming. The hard constraints of the instance (round robin structure, phases, CA1 to CA4, GA1, BR1, BR2) are posted directly on binary game variables x[home,away,slot] plus home and break indicators, with no objective. OR-Tools CP-SAT runs its default portfolio with 8 workers and a fixed seed until a feasible timetable is found or the time limit of 600 s expires. Soft constraints are ignored, as the benchmark specifies. Every timetable is checked by an independent checker before it is reported. |
| Algorithm Type | Stochastic |
| Paradigm | Classical |
| # Runs | 5 |
| # Feasible Runs | 5 |
| # Successful Runs | 5 |
| Success Threshold | 0 |
| ====== |  |
| Hardware Specifications | Apple M3 Pro (Mac15,6), 11 cores (5 performance + 6 efficiency), 18 GB unified memory, arm64, macOS 26.3, on AC power; Python 3.11.7, OR-Tools 9.14.6206. Runs executed strictly one at a time; 40 runs that overlapped other work on the machine were discarded and run again with the same seed. With 8 workers and 5 performance cores, part of the work runs on the efficiency cores. |
| ====== |  |
| Total Runtime | 0.02 |
| Time to Solution | 0.02 |
| CPU Runtime | 0.01 |
| GPU Runtime | N/A |
| QPU Runtime | N/A |
| Other HW Runtime | N/A |
| ====== |  |
| Remarks | Reaches the table value 0 (optimal). Pure feasibility problem: the objective is 0 for any timetable that satisfies all hard constraints, so 0 is also the bound. 6 teams, 10 slots, phased, 102 hard constraints. 5 independent runs, CP-SAT seeds 0, 1, 2, 3, 4, 8 workers and a 600 s limit each, strictly one run at a time; 5 of 5 found a timetable. Wall clock per run, model build included: 0.0 s, 0.0 s, 0.0 s, 0.0 s, 0.0 s. Time to Solution is the mean wall clock time of the runs that found a timetable. Total Runtime is the mean wall clock time and CPU Runtime the mean process CPU time over all runs; CPU time adds up all CP-SAT worker threads, so with 8 workers it is up to about 8 times the wall clock time. Runs of a fraction of a second are partly idle (for example while the worker threads start and stop), so CPU time can come out below wall clock time. Runtimes are rounded to 0.01 s here and to 0.1 s in the list above (runs without a timetable to 1 s). The solution file is the timetable of the fastest run. Checked with an independent checker that accepts all 249 reference solutions in 05-sports/solutions. |
