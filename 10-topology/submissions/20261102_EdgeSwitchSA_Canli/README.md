# Edge-switch annealing for the order/degree problem

Submitter: Arhan Canli (Quantavane), 2026-11-02.

Code, independent checker and the exact command of every run: https://github.com/arhancanli/quantavane-qoblib

## Results

Every instance of the class was run with the same method and five seeds (1-5), except four instances too large for
this method (listed below). "Ours" is the best diameter over the five runs. "Lower bound" is the Moore bound, which
the method computes in every run (it is the Optimality Bound in the CSV files); where ours equals it, the run stopped
there and the graph is proven optimal. Times are CPU seconds. All runs are reported in the CSV files and the
objective time series.

| Instance | n | d | Listed best (status) | Ours | Lower bound | Proven optimal | Runs reaching it | Mean time to it | Compared with the listed value |
| :------- | -: | -: | :------------------ | ---: | ----------: | :------------: | :--------------: | --------------: | :----------------------------- |
| topology_15_3 | 15 | 3 | 3 (optimal) | 3 | 3 | yes | 5 / 5 | 0.00 s | matched |
| topology_15_4 | 15 | 4 | 2 (optimal) | 2 | 2 | yes | 5 / 5 | 0.06 s | matched |
| topology_20_3 | 20 | 3 | 3 (optimal) | 3 | 3 | yes | 5 / 5 | 0.00 s | matched |
| topology_20_4 | 20 | 4 | 3 (optimal) | 3 | 3 | yes | 5 / 5 | 0.00 s | matched |
| topology_20_5 | 20 | 5 | 2 (optimal) | 2 | 2 | yes | 5 / 5 | 1.14 s | matched |
| topology_25_3 | 25 | 3 | 4 (optimal) | 4 | 4 | yes | 5 / 5 | 0.00 s | matched |
| topology_25_4 | 25 | 4 | 3 (optimal) | 3 | 3 | yes | 5 / 5 | 0.00 s | matched |
| topology_25_5 | 25 | 5 | 3 (optimal) | 3 | 2 | no | 5 / 5 | 0.00 s | matched |
| topology_25_6 | 25 | 6 | 2 (optimal) | 2 | 2 | yes | 5 / 5 | 1.78 s | matched |
| topology_30_4 | 30 | 4 | 3 (optimal) | 3 | 3 | yes | 5 / 5 | 0.19 s | matched |
| topology_30_5 | 30 | 5 | 3 (optimal) | 3 | 3 | yes | 5 / 5 | 0.00 s | matched |
| topology_30_6 | 30 | 6 | 3 (best known) | 2 | 2 | yes | 5 / 5 | 20.97 s | improved |
| topology_35_5 | 35 | 5 | 4 (best known) | 3 | 3 | yes | 5 / 5 | 0.00 s | improved |
| topology_35_6 | 35 | 6 | 3 (best known) | 3 | 2 | no | 5 / 5 | 0.00 s | matched |
| topology_40_6 | 40 | 6 | 3 (optimal) | 3 | 3 | yes | 5 / 5 | 0.00 s | matched |
| topology_50_4 | 50 | 4 | 5 (best known) | 4 | 3 | no | 5 / 5 | 0.00 s | improved |
| topology_512_4 | 512 | 4 | 6 (best known) | 7 | 6 | no | 5 / 5 | 0.02 s | worse |
| topology_512_6 | 512 | 6 | 5 (best known) | 5 | 4 | no | 5 / 5 | 0.02 s | matched |
| topology_1024_4 | 1024 | 4 | 7 (best known) | 8 | 6 | no | 5 / 5 | 0.03 s | worse |
| topology_1726_30 | 1726 | 30 | 3 (best known) | 3 | 3 | yes | 5 / 5 | 0.08 s | matched |
| topology_4855_15 | 4855 | 15 | 4 (best known) | 5 | 4 | no | 5 / 5 | 0.07 s | worse |
| topology_9344_6 | 9344 | 6 | 7 (best known) | 8 | 6 | no | 5 / 5 | 0.09 s | worse |

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
- Lower bound, computed in every run: the Moore bound. A graph of maximum degree d and diameter k has at most
  1 + d + d(d-1) + ... + d(d-1)^(k-1) nodes, so the diameter is at least the smallest k for which this reaches n
  (1 only when d >= n - 1, the complete graph). The target never goes below this bound, and a run stops as soon as
  the incumbent equals it: the graph is then proven optimal.
- Otherwise a run ends when its CPU time reaches the budget, or after the stall limit (CPU seconds without a new
  incumbent). No known value is used.

## Run protocol

- Seeds 1 to 5 for every instance.
- n <= 50: budget 150 s CPU, stall 60 s CPU, 10,000,000 moves per cooling round.
- n >= 512: budget 120 s CPU, stall 60 s CPU, rounds of 200,000 / 50,000 / 10,000 / 3,000 / 1,000 moves for
  n = 512 / 1024 / 1726 / 4855 / 9344, so that a cooling round fits in the budget.
- Each instance's objective time series file holds its five runs (seeds 1 to 5 in order): the start graph, every new
  incumbent and the end of the run, with times in CPU seconds. The solution file is the graph of the first seed that
  reached the best diameter.

## Timing: runtimes without waiting

Every run is a single-threaded process. The runs shared an 18-core Mac with other jobs (load about 70 to 150) at
nice 10, so the wall clock also counted time a process spent waiting for a free core. Every time reported here is
therefore the process's own CPU time (user plus system, measured by the program), which is the time the run takes
when it has a core to itself and excludes all waiting. Total Runtime, Time to Solution and CPU Runtime in the CSV
files and the times in the objective time series are all CPU times. Total Runtime equals CPU Runtime, since nothing
else ran for the method. Budgets and stall limits are counted in CPU seconds too.

## Optimality Bound

The Optimality Bound in every CSV is the Moore lower bound computed by the method, as described above. Where the
best diameter equals it, the result is proven optimal by the run itself; the table shows which. For topology_50_4
the bound is 3 and ours is 4: diameter 3 would need a 50-node graph of degree at most 4 and diameter 3, and the
largest such graph known has 41 nodes, so 4 is very likely optimal but not proven here.

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
