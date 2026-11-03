# Edge-switch annealing for the order/degree problem

Submitter: Arhan Canli (Quantavane), 2026-11-02.

Code, independent checker and the exact command of every run: https://github.com/arhancanli/quantavane-qoblib

## Results

Every instance of the class was run with the same method and five seeds (1-5), except four instances too large for
this method (listed below). "Ours" is the best diameter over the five runs; all runs are reported in the CSV files
and the objective time series.

| Instance | n | d | Listed best (status) | Ours | Runs reaching it | Mean time to it | Compared with the listed value |
| :------- | -: | -: | :------------------ | ---: | :--------------: | --------------: | :----------------------------- |
| topology_15_3 | 15 | 3 | 3 (optimal) | 3 | 5 / 5 | 0.0 s | matched |
| topology_15_4 | 15 | 4 | 2 (optimal) | 2 | 5 / 5 | 0.1 s | matched |
| topology_20_3 | 20 | 3 | 3 (optimal) | 3 | 5 / 5 | 0.0 s | matched |
| topology_20_4 | 20 | 4 | 3 (optimal) | 3 | 5 / 5 | 0.0 s | matched |
| topology_20_5 | 20 | 5 | 2 (optimal) | 2 | 5 / 5 | 2.6 s | matched |
| topology_25_3 | 25 | 3 | 4 (optimal) | 4 | 5 / 5 | 0.0 s | matched |
| topology_25_4 | 25 | 4 | 3 (optimal) | 3 | 5 / 5 | 0.0 s | matched |
| topology_25_5 | 25 | 5 | 3 (optimal) | 3 | 5 / 5 | 0.0 s | matched |
| topology_25_6 | 25 | 6 | 2 (optimal) | 2 | 5 / 5 | 4.2 s | matched |
| topology_30_4 | 30 | 4 | 3 (optimal) | 3 | 5 / 5 | 0.3 s | matched |
| topology_30_5 | 30 | 5 | 3 (optimal) | 3 | 5 / 5 | 0.0 s | matched |
| topology_30_6 | 30 | 6 | 3 (best known) | 2 | 5 / 5 | 51.1 s | improved |
| topology_35_5 | 35 | 5 | 4 (best known) | 3 | 5 / 5 | 0.0 s | improved |
| topology_35_6 | 35 | 6 | 3 (best known) | 3 | 5 / 5 | 0.0 s | matched |
| topology_40_6 | 40 | 6 | 3 (optimal) | 3 | 5 / 5 | 0.0 s | matched |
| topology_50_4 | 50 | 4 | 5 (best known) | 4 | 5 / 5 | 0.0 s | improved |
| topology_512_4 | 512 | 4 | 6 (best known) | 7 | 5 / 5 | 0.0 s | worse |
| topology_512_6 | 512 | 6 | 5 (best known) | 5 | 5 / 5 | 0.0 s | matched |
| topology_1024_4 | 1024 | 4 | 7 (best known) | 8 | 5 / 5 | 0.0 s | worse |
| topology_1726_30 | 1726 | 30 | 3 (best known) | 3 | 5 / 5 | 0.1 s | matched |
| topology_4855_15 | 4855 | 15 | 4 (best known) | 5 | 5 / 5 | 0.1 s | worse |
| topology_9344_6 | 9344 | 6 | 7 (best known) | 8 | 5 / 5 | 0.1 s | worse |

Not run:

| Instance | n | d | Listed best (status) | Reason |
| :------- | -: | -: | :------------------ | :----- |
| topology_65536_6 | 65536 | 6 | 9 (best known) | not run: the all-pairs distance bitsets need n^2/4 bytes (1.1 GB) and every move costs O(n^2 d / 64) |
| topology_100000_8 | 100000 | 8 | 7 (best known) | not run: the all-pairs distance bitsets need n^2/4 bytes (2.5 GB) and every move costs O(n^2 d / 64) |
| topology_1000000_16 | 1000000 | 16 | 6 (best known) | not run: the all-pairs distance bitsets need n^2/4 bytes (250.0 GB) and every move costs O(n^2 d / 64) |
| topology_1000000_32 | 1000000 | 32 | 5 (best known) | not run: the all-pairs distance bitsets need n^2/4 bytes (250.0 GB) and every move costs O(n^2 d / 64) |

## Method

A direct search over graphs; no MIP or QUBO model (program `src/qob_topo.c` in the repository above).

- Degrees are fixed at d (one node at d - 1 when n*d is odd). The start is a circulant graph (offsets 1..floor(d/2),
  plus the antipodal matching when d is odd), scrambled by 20 |E| random degree-preserving switches. Its diameter is
  the first incumbent.
- Move: a switch. Two edges (a,b) and (c,e) become (a,c) and (b,e), or (a,e) and (b,c), when both new edges are new
  and not loops. Degrees never change.
- Target D = incumbent - 1. Cost: with R_k(v) the set of nodes within distance k of v, kept as bitsets and grown level
  by level, cost = far + near, where far = sum over v of (n - |R_D(v)|) counts ordered pairs further apart than D and
  near = sum over k = 1..D-1 of sum over v of (n - |R_k(v)|).
- Simulated annealing (Metropolis acceptance), geometric cooling from T = 8 to T = 0.5 over one round of moves, each
  round restarting from the best graph of the previous one. A graph with far = 0 has diameter at most D: its exact
  diameter becomes the new incumbent and the target drops by one.
- A run ends when its CPU time reaches the budget, or after the stall limit (CPU seconds without a new incumbent).
  No bound or known value is used to stop.

## Run protocol

- Seeds 1 to 5 for every instance.
- n <= 50: budget 150 s CPU, stall 60 s CPU, 10,000,000 moves per cooling round.
- n >= 512: budget 120 s CPU, stall 60 s CPU, rounds of 200,000 / 50,000 / 10,000 / 3,000 / 1,000 moves for
  n = 512 / 1024 / 1726 / 4855 / 9344, so that a cooling round fits in the budget.
- Each instance's objective time series file holds its five runs (seeds 1 to 5 in order): the start graph, every new
  incumbent and the end of the run, with wall-clock times. The solution file is the graph of the first seed that
  reached the best diameter.

## Timing: why CPU time is below total runtime

The runs shared an 18-core Mac with other jobs (load about 70 to 80) and ran at nice 10. For much of each run the
process was ready but waiting for a free core, so its CPU time (user plus system) is lower than its wall-clock time.
Nothing else happened in the rest of that time. Budgets are counted in CPU seconds, so a run does the same work
however busy the machine is. In the CSV files, Total Runtime and Time to Solution are wall-clock times, as QOBLIB
defines them, and CPU Runtime is process CPU time.

## Optimality Bound

`N/A` in every CSV: the method computes no bound. A separate argument, not part of the method: a graph of maximum
degree d and diameter k has at most 1 + d + d(d-1) + ... + d(d-1)^(k-1) nodes (the Moore bound). So topology_30_6
cannot have diameter 1 (at most 7 nodes), and topology_35_5 and topology_50_4 cannot have diameter 2 (at most 26
and 17 nodes). The diameters 2 for topology_30_6 and 3 for topology_35_5 are therefore optimal. For topology_50_4,
diameter 3 would need a 50-node graph of degree at most 4 and diameter 3; the largest such graph known has 41 nodes.

## Verification

The final graph of every run was re-checked by `check/check.py` in the repository above. It is a program written
separately from the search (Python, breadth-first search from every node), and it checks the node count, loops and
repeated edges, the maximum degree, connectivity and the diameter.

## Hardware and software

Apple M5 Pro (18 cores: 6 performance, 12 efficiency), 24 GB RAM, macOS 26.6.2. Search in C, compiled with
Apple clang 21.0.0 at -O3, one single-threaded process per run. Checker: Python 3.9.6.

## AI disclosure

generated: the search program (C), the checking program (Python) and this write-up were written with Claude
(Anthropic), model Claude Opus 5.5 (claude-opus-5-5), in Claude Code, and reviewed by the submitter, who takes
responsibility for the submission. Every solution was checked by the independent program described above. The
pull request was opened by the submitter.
