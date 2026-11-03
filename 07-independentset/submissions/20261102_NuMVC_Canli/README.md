# NuMVC-style vertex cover local search for maximum stable sets

Submitter: Arhan Canli (Quantavane), 2026-11-02.

Code, independent checker and the exact command of every run: https://github.com/arhancanli/quantavane-qoblib

## Results

Every instance of the class was run with the same method: five runs of 30 seconds each (seeds 1 to 5). On the two
frb instances where we went beyond the listed value there were also longer runs, reported as extra CSV rows and
listed in the last column. "Ours" is the best stable set over the five 30-second runs. Every run is in the CSV files
and the objective time series.

| Instance | n | Listed best (status) | Ours (30 s) | Runs reaching it | Compared with the listed value | Longer runs |
| :------- | -: | :------------------ | ----------: | :--------------: | :----------------------------- | :---------- |
| aves-sparrow-social | 52 | 13 (optimal) | 13 | 5 / 5 | matched | |
| brock200-1 | 200 | 6 (optimal) | 6 | 5 / 5 | matched | |
| brock200-2 | 200 | 12 (optimal) | 12 | 5 / 5 | matched | |
| brock200-3 | 200 | 9 (optimal) | 9 | 5 / 5 | matched | |
| brock200-4 | 200 | 8 (optimal) | 8 | 5 / 5 | matched | |
| brock400-1 | 400 | 27 (optimal) | 25 | 5 / 5 | below | |
| brock800-1 | 800 | 23 (optimal) | 21 | 5 / 5 | below | |
| c-fat200-1 | 200 | 18 (optimal) | 18 | 5 / 5 | matched | |
| C125-9 | 125 | 34 (optimal) | 34 | 5 / 5 | matched | |
| C4000-5 | 4000 | 18 (best known) | 17 | 5 / 5 | below | |
| C500-9 | 500 | 57 (best known) | 57 | 5 / 5 | matched | |
| chesapeake | 39 | 17 (optimal) | 17 | 5 / 5 | matched | |
| es60fst01 | 123 | 60 (optimal) | 60 | 5 / 5 | matched | |
| es60fst02 | 186 | 88 (optimal) | 88 | 5 / 5 | matched | |
| es60fst03 | 113 | 55 (optimal) | 55 | 5 / 5 | matched | |
| es60fst04 | 162 | 78 (optimal) | 78 | 5 / 5 | matched | |
| farm | 17 | 10 (optimal) | 10 | 5 / 5 | matched | |
| football | 35 | 16 (optimal) | 16 | 5 / 5 | matched | |
| frb100-40 | 4000 | 96 (best known) | 95 | 1 / 5 | below | longer runs: 97 (4 / 5 runs), 97 (1 / 2 runs) |
| frb45-21-3 | 945 | 45 (optimal) | 45 | 4 / 5 | matched | |
| frb50-23-3 | 1150 | 50 (optimal) | 49 | 5 / 5 | below | |
| frb53-24-1 | 1272 | 53 (best known) | 52 | 5 / 5 | below | |
| frb59-26-2 | 1534 | 58 (best known) | 58 | 3 / 5 | matched | longer runs: 59 (1 / 5 runs) |
| gen200_p0-9_44 | 200 | 44 (optimal) | 44 | 5 / 5 | matched | |
| hamming10-4 | 1024 | 40 (best known) | 40 | 5 / 5 | matched | |
| hamming6-2 | 64 | 2 (optimal) | 2 | 5 / 5 | matched | |
| hamming6-4 | 64 | 12 (optimal) | 12 | 5 / 5 | matched | |
| ibm32 | 32 | 13 (optimal) | 13 | 5 / 5 | matched | |
| insecta-ant-colony1-day38 | 56 | 6 (optimal) | 6 | 5 / 5 | matched | |
| insecta-ant-colony3-day09 | 160 | 9 (optimal) | 9 | 5 / 5 | matched | |
| johnson16-2-4 | 120 | 15 (optimal) | 15 | 5 / 5 | matched | |
| johnson8-2-4 | 28 | 7 (optimal) | 7 | 5 / 5 | matched | |
| johnson8-4-4 | 70 | 5 (optimal) | 5 | 5 / 5 | matched | |
| karate | 34 | 20 (optimal) | 20 | 5 / 5 | matched | |
| keller4 | 171 | 11 (optimal) | 11 | 5 / 5 | matched | |
| keller6 | 3361 | 59 (best known) | 59 | 5 / 5 | matched | |
| mammalia-kangaroo-interactions | 17 | 4 (optimal) | 4 | 5 / 5 | matched | |
| MANN-a9 | 45 | 3 (optimal) | 3 | 5 / 5 | matched | |
| p_hat1500-1 | 1500 | 12 (optimal) | 12 | 5 / 5 | matched | |
| p_hat1500-3 | 1500 | 94 (optimal) | 94 | 5 / 5 | matched | |
| R_1000_005_1 | 1000 | 117 (best known) | 117 | 5 / 5 | matched | |
| R_500_005_1 | 500 | 91 (best known) | 91 | 5 / 5 | matched | |
| sloane_1dc_128 | 128 | 16 (optimal) | 16 | 5 / 5 | matched | |
| sloane_1dc_64 | 64 | 10 (optimal) | 10 | 5 / 5 | matched | |
| sloane_1zc_128 | 128 | 18 (optimal) | 18 | 5 / 5 | matched | |
| sloane_2dc_128 | 128 | 5 (optimal) | 5 | 5 / 5 | matched | |
| socfb-haverford76 | 1446 | 282 (best known) | 282 | 5 / 5 | matched | |
| socfb-trinity100 | 2613 | 499 (best known) | 499 | 5 / 5 | matched | |
| sorrell4 | 2048 | 24 (optimal) | 24 | 5 / 5 | matched | |
| sorrell7 | 2048 | 198 (best known) | 198 | 5 / 5 | matched | |

## Method

A stable set is found as the complement of a vertex cover; no MIP or QUBO model (program `src/qob_numvc.c` in the
repository above). The search follows NuMVC (Cai, Su, Luo and Sattar, "NuMVC: an efficient local search algorithm
for minimum vertex cover", JAIR 46, 2013):

- Start: a greedy cover (a random uncovered edge gets its endpoint with the larger score), then redundant vertices
  are dropped.
- Whenever the current set C covers every edge it is recorded, and the vertex of C with the highest score is removed,
  so the search then looks for a cover one vertex smaller.
- Each step removes the vertex u of C with the highest score (oldest on ties; never the vertex added in the step
  before), then picks a random uncovered edge and adds the endpoint whose configuration changed since it last left C
  (configuration checking), the higher score first, the older one on ties.
- Scores use edge weights: each step adds 1 to the weight of every uncovered edge; when the mean weight reaches
  gamma = n/2 every weight becomes floor(0.3 * w) (at least 1) and the scores are rebuilt.
- A run ends at its wall-clock limit. No bound is computed.

## Run protocol

- All instances: seeds 1 to 5, 30 seconds of wall-clock time per run. 54 of these 250 runs, all on small
  instances, were made twice. The first build did not save the starting set when it was already the run's best, so
  those runs were repeated with a build that saves it; the search is the same, and the repeats are the runs
  reported.
- frb59-26-2, longer runs (made first, with an earlier build of the same search): seed 1 had a 3600 s limit and was
  ended by hand at 1186 s, after it had reached 59 at 1086 s; seeds 2 to 5 had 1800 s limits and were set to end
  early at 59, which none of them reached.
- frb100-40, longer runs (earlier builds of the same search): seeds 1 to 5 with 3600 s limits, and seeds 6 and 7 with
  7200 s limits.
- Each instance's objective time series file holds all its runs in the order of the CSV rows (30-second runs, seeds
  1 to 5, then the longer runs in seed order): the first set, every improvement and the end of the run, with
  wall-clock times. The earlier builds wrote no time-series file; their series were rebuilt from the run logs, which
  record every new best set with its time. The solution file is the set of the first run that reached the best size.

## Timing: why CPU time is below total runtime

The runs shared an 18-core Mac with other jobs (load about 70 to 80) and ran at nice 10. For much of each run the
process was ready but waiting for a free core, so its CPU time (user plus system) is lower than its wall-clock time.
Nothing else happened in the rest of that time. In the CSV files, Total Runtime and Time to Solution are wall-clock
times, as QOBLIB defines them, and CPU Runtime is process CPU time. Two of the longer runs (seed 1 on each frb
instance) were made before CPU timing was added; the CSV says so and averages CPU time over the other runs.

## Optimality Bound

`N/A` in every CSV: the method computes no bound. A separate argument, not part of the method: frb59-26-2 and
frb100-40 are model RB (BHOSLIB) instances whose nodes split into disjoint cliques of consecutive nodes (59 cliques of
26 and 100 cliques of 40; checked on the instance files). A stable set holds at most one node of each clique, so 59
is optimal for frb59-26-2 and 100 bounds frb100-40.

## Verification

Every stable set that was saved (each 30-second run's best set, and the sets of the longer runs that reached the
listed value or beyond) was re-checked by `check/check.py` in the repository above. It is a program written
separately from the search (Python): every index in range, no repeats, and no edge of the instance with both
endpoints in the set.

## Hardware and software

Apple M5 Pro (18 cores: 6 performance, 12 efficiency), 24 GB RAM, macOS 26.6.2. Search in C, compiled with
Apple clang 21.0.0 at -O3, one single-threaded process per run. Checker: Python 3.9.6.

## AI disclosure

generated: the search program (C), the checking program (Python) and this write-up were written with Claude
(Anthropic), model Claude Opus 5.5 (claude-opus-5-5), in Claude Code, and reviewed by the submitter, who takes
responsibility for the submission. Every solution was checked by the independent program described above. The
pull request was opened by the submitter.
