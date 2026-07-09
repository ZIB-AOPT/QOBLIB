# Submission for XSH-n20-k4-13

This directory contains the submission for the problem **XSH-n20-k4-13**.

| Field | Value 1 |
| --- | --- |
| Problem | XSH-n20-k4-13 |
| Submitter | Othmane El Yaakoubi |
| Affiliation | Independent Researcher |
| Date | 2026-07-08 |
| ====== |  |
| Reference | Code: https://github.com/othma125/heuristicCVRP |
| Best Objective Value | 628 |
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
| ====== |  |
| Workflow | Pre-processing: parse CVRPLIB instance, build rounded-Euclidean (EUC_2D) distances. Main optimization: graph-based genetic algorithm on a giant-tour chromosome, decoded via a directed acyclic graph whose shortest path gives the optimal capacity-feasible split; tournament selection, optimization-driven graph-based crossover, and mutation, with intra- and inter-route local search (2-opt, segment reversal, customer reallocation) embedded inside the graph. Post-processing: return the best feasible split found. |
| Algorithm Type | Stochastic |
| Paradigm | Classical |
| # Runs | 1 |
| # Feasible Runs | 1 |
| # Successful Runs | 1 |
| Success Threshold | 0 |
| ====== |  |
| Hardware Specifications | Intel Core i7-7700HQ @ 2.80GHz (4 cores / 8 threads); 16 GB RAM; Ubuntu 24.04 LTS; Java 21 (Oracle GraalVM 21.0.2), multi-threaded execution |
| ====== |  |
| Total Runtime | 36.463 |
| Time to Solution | 18.579 |
| CPU Runtime | 36.463 |
| GPU Runtime | 0 |
| QPU Runtime | 0 |
| Other HW Runtime | 0 |
| ====== |  |
| Remarks | Single run of a stochastic graph-based genetic algorithm. Known optimal = 628; gap = 0.0%. Time to Solution is the timestamp of the last logged incumbent improvement in that run. |
