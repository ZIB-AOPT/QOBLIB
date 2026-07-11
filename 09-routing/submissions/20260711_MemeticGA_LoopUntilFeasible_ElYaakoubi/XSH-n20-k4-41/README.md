# Submission for XSH-n20-k4-41

This directory contains the submission for the problem **XSH-n20-k4-41**.

| Field | Value 1 |
| --- | --- |
| Problem | XSH-n20-k4-41 |
| Submitter | Othmane El Yaakoubi |
| Affiliation | Independent Researcher |
| Date | 2026-07-11 |
| ====== |  |
| Reference | Code: https://github.com/othma125/heuristicCVRP |
| Best Objective Value | 736 |
| Optimality Bound | N/A |
| ====== |  |
| Modeling Approach | Giant-tour (permutation) representation with graph-based optimal split into capacity-feasible routes |
| # Decision Variables | 20 |
| # Binary Variables | 0 |
| # Integer Variables | 20 |
| # Continuous Variables | 0 |
| # Non-Zero Coefficients | N/A |
| Coefficients Type | integer |
| Coefficients Range | N/A - N/A |
| Workflow | Pre-processing: parse CVRPLIB instance, build rounded-Euclidean (EUC_2D) distances. Main optimization: loop-until-feasible wrapper around a graph-based genetic algorithm on a giant-tour chromosome, decoded via a directed acyclic graph whose shortest path gives the optimal capacity-feasible split; tournament selection, optimization-driven graph-based crossover, and mutation, with intra- and inter-route local search (2-opt, segment reversal, customer reallocation) embedded inside the graph. Because a feasible capacity split is not guaranteed from a random start under the tight k=4 capacity, each run restarts from a fresh random population until it returns a feasible solution. Post-processing: return the best feasible split found. |
| Algorithm Type | Stochastic |
| Paradigm | Classical |
| # Runs | 5 |
| # Feasible Runs | 5 |
| # Successful Runs | 1 |
| Success Threshold | 736 |
| ====== |  |
| Hardware Specifications | Intel Core i7-7700HQ @ 2.80GHz (4 cores / 8 threads); 16 GB RAM; Ubuntu 24.04 LTS; Java 21 (Oracle GraalVM 21.0.2), multi-threaded execution |
| ====== |  |
| Total Runtime | 36.073 |
| Time to Solution | 25.272 |
| CPU Runtime | 36.073 |
| GPU Runtime | 0 |
| QPU Runtime | 0 |
| Other HW Runtime | 0 |
| ====== |  |
| Remarks | Loop-until-feasible variant: each run restarts from a fresh random population until it returns a capacity-feasible solution, so all runs are feasible by construction. Attempts to feasibility over the 5 runs: mean 3.4 (min 3, max 5). Known optimal = 736; best gap = 0.00%. Total Runtime and Time to Solution are wall-clock and include the failed-attempt retries; TTS is measured from the meta-run start to the last incumbent improvement. |
