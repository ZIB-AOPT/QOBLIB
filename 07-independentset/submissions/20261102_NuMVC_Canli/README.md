# NuMVC-style vertex cover local search for maximum stable sets

Submitter: Arhan Canli (Quantavane), 2026-11-02.

| Instance | Stable set found | Previous best known | Upper bound | Runs reaching it |
| :------- | ---------------: | ------------------: | ----------: | :--------------: |
| frb59-26-2 | 59 | 58 | 59 | 1 / 5 |
| frb100-40 | 97 | 96 | 100 | 4 / 5 |

Both are model RB instances (BHOSLIB, frbN-K): the nodes split into N disjoint cliques of K consecutive nodes (checked on the instance files), so a stable set has at most N nodes. 59 is therefore optimal for frb59-26-2; for frb100-40 the bound is 100 (a stable set of 100 is hidden by construction), and 97 is not claimed optimal.

## Method

A stable set is found as the complement of a vertex cover; no MIP or QUBO model. The search follows NuMVC (Cai,
Su, Luo and Sattar, "NuMVC: an efficient local search algorithm for minimum vertex cover", JAIR 46, 2013):

- Start: a greedy cover (a random uncovered edge gets its endpoint with the larger score), then redundant vertices
  are dropped.
- Whenever the current set C covers every edge it is recorded, and the vertex of C with the highest score is
  removed, so the search then looks for a cover one vertex smaller.
- Each step removes the vertex u of C with the highest score (oldest on ties; never the vertex added in the step
  before), then picks a random uncovered edge and adds the endpoint whose configuration changed since it last left C
  (configuration checking), the higher score first, the older one on ties.
- Scores use edge weights: each step adds 1 to the weight of every uncovered edge; when the mean weight reaches
  gamma = n/2 every weight becomes floor(0.3 * w) (at least 1) and the scores are rebuilt.
- A run ends at its time limit, or as soon as the stable set reaches a known upper bound.

Runs (seed: time to reach the reported size, wall clock on a shared machine):

- frb59-26-2 (limit 1800 s per run): seed 1: 59 at 1086 s, seed 2: best 58 in 1800 s, seed 3: best 58 in 1800 s, seed 4: best 58 in 1800 s, seed 5: best 58 in 1800 s.
- frb100-40 (limit 3600 s per run): seed 1: 97 at 2517 s, seed 2: 97 at 1811 s, seed 3: 97 at 850 s, seed 4: best 96 in 3600 s, seed 5: 97 at 1532 s.

Parameters gamma = n/2, rho = 0.3 in every run.

## Verification

Every stable set was checked twice: by the search itself (every edge has an endpoint in the cover) and by a
separate program written independently of the search (Python): every index in range, no repeats, and no edge of the
instance with both endpoints in the set.

## Hardware and software

Apple M5 Pro (18 cores: 6 performance, 12 efficiency), 24 GB RAM, macOS 26.6.2. Search in C, compiled with
Apple clang 21.0.0 at -O3; one single-threaded process per run on a shared machine (nice 10), so wall-clock times
include contention. Checker: Python 3.9.6.

## AI disclosure

generated: the search program (C), the checking program (Python) and this write-up were written with Claude
(Anthropic), model Claude Opus 5.5 (claude-opus-5-5), in Claude Code, and reviewed by the submitter, who takes
responsibility for the submission. Every solution was checked by the independent program described above. The
pull request was opened by the submitter.
