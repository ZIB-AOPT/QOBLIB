# NuMVC-style vertex cover local search for maximum stable sets

Submitter: Arhan Canli (Quantavane), 2026-11-02.

Code, independent checker and the exact command of every run: https://github.com/arhancanli/quantavane-qoblib

## Results

Every instance of the class was run with the same method: five runs of 30 seconds of CPU time each (seeds 1 to 5).
On the two frb instances where we went beyond the listed value there were also longer runs, reported as an extra
CSV row and summarized in the last column. "Ours" is the best stable set over the five 30-second runs. "Upper bound"
is the greedy clique-cover bound, which the method computes in every run (it is the Optimality Bound in the CSV
files); where ours equals it, the run stopped there and the set is proven optimal. Every run is in the CSV files and
the objective time series.

| Instance | n | Listed best (status) | Ours (30 s) | Upper bound | Proven optimal | Runs reaching it | Compared with the listed value | Longer runs |
| :------- | -: | :------------------ | ----------: | ----------: | :------------: | :--------------: | :----------------------------- | :---------- |
| aves-sparrow-social | 52 | 13 (optimal) | 13 | 13 | yes | 5 / 5 | matched | |
| brock200-1 | 200 | 6 (optimal) | 6 | 17 | no | 5 / 5 | matched | |
| brock200-2 | 200 | 12 (optimal) | 12 | 30 | no | 5 / 5 | matched | |
| brock200-3 | 200 | 9 (optimal) | 9 | 24 | no | 5 / 5 | matched | |
| brock200-4 | 200 | 8 (optimal) | 8 | 21 | no | 5 / 5 | matched | |
| brock400-1 | 400 | 27 (optimal) | 25 | 85 | no | 5 / 5 | below | |
| brock800-1 | 800 | 23 (optimal) | 21 | 117 | no | 5 / 5 | below | |
| c-fat200-1 | 200 | 18 (optimal) | 18 | 19 | no | 5 / 5 | matched | |
| C125-9 | 125 | 34 (optimal) | 34 | 49 | no | 5 / 5 | matched | |
| C4000-5 | 4000 | 18 (best known) | 17 | 330 | no | 5 / 5 | below | |
| C500-9 | 500 | 57 (best known) | 57 | 151 | no | 5 / 5 | matched | |
| chesapeake | 39 | 17 (optimal) | 17 | 17 | yes | 5 / 5 | matched | |
| es60fst01 | 123 | 60 (optimal) | 60 | 63 | no | 5 / 5 | matched | |
| es60fst02 | 186 | 88 (optimal) | 88 | 93 | no | 5 / 5 | matched | |
| es60fst03 | 113 | 55 (optimal) | 55 | 59 | no | 5 / 5 | matched | |
| es60fst04 | 162 | 78 (optimal) | 78 | 82 | no | 5 / 5 | matched | |
| farm | 17 | 10 (optimal) | 10 | 11 | no | 5 / 5 | matched | |
| football | 35 | 16 (optimal) | 16 | 17 | no | 5 / 5 | matched | |
| frb100-40 | 4000 | 96 (best known) | 96 | 100 | no | 2 / 5 | matched | 97 (5 / 7 runs) |
| frb45-21-3 | 945 | 45 (optimal) | 45 | 45 | yes | 5 / 5 | matched | |
| frb50-23-3 | 1150 | 50 (optimal) | 49 | 50 | no | 5 / 5 | below | |
| frb53-24-1 | 1272 | 53 (best known) | 52 | 53 | no | 5 / 5 | below | |
| frb59-26-2 | 1534 | 58 (best known) | 58 | 59 | no | 5 / 5 | matched | 59 (1 / 5 runs, proven optimal) |
| gen200_p0-9_44 | 200 | 44 (optimal) | 44 | 45 | no | 5 / 5 | matched | |
| hamming10-4 | 1024 | 40 (best known) | 40 | 83 | no | 5 / 5 | matched | |
| hamming6-2 | 64 | 2 (optimal) | 2 | 2 | yes | 5 / 5 | matched | |
| hamming6-4 | 64 | 12 (optimal) | 12 | 16 | no | 5 / 5 | matched | |
| ibm32 | 32 | 13 (optimal) | 13 | 14 | no | 5 / 5 | matched | |
| insecta-ant-colony1-day38 | 56 | 6 (optimal) | 6 | 8 | no | 5 / 5 | matched | |
| insecta-ant-colony3-day09 | 160 | 9 (optimal) | 9 | 14 | no | 5 / 5 | matched | |
| johnson16-2-4 | 120 | 15 (optimal) | 15 | 15 | yes | 5 / 5 | matched | |
| johnson8-2-4 | 28 | 7 (optimal) | 7 | 7 | yes | 5 / 5 | matched | |
| johnson8-4-4 | 70 | 5 (optimal) | 5 | 6 | no | 5 / 5 | matched | |
| karate | 34 | 20 (optimal) | 20 | 21 | no | 5 / 5 | matched | |
| keller4 | 171 | 11 (optimal) | 11 | 24 | no | 5 / 5 | matched | |
| keller6 | 3361 | 59 (best known) | 59 | 164 | no | 5 / 5 | matched | |
| mammalia-kangaroo-interactions | 17 | 4 (optimal) | 4 | 4 | yes | 5 / 5 | matched | |
| MANN-a9 | 45 | 3 (optimal) | 3 | 3 | yes | 5 / 5 | matched | |
| p_hat1500-1 | 1500 | 12 (optimal) | 12 | 87 | no | 5 / 5 | matched | |
| p_hat1500-3 | 1500 | 94 (optimal) | 94 | 294 | no | 5 / 5 | matched | |
| R_1000_005_1 | 1000 | 117 (best known) | 117 | 331 | no | 5 / 5 | matched | |
| R_500_005_1 | 500 | 91 (best known) | 91 | 184 | no | 5 / 5 | matched | |
| sloane_1dc_128 | 128 | 16 (optimal) | 16 | 22 | no | 5 / 5 | matched | |
| sloane_1dc_64 | 64 | 10 (optimal) | 10 | 13 | no | 5 / 5 | matched | |
| sloane_1zc_128 | 128 | 18 (optimal) | 18 | 28 | no | 5 / 5 | matched | |
| sloane_2dc_128 | 128 | 5 (optimal) | 5 | 6 | no | 5 / 5 | matched | |
| socfb-haverford76 | 1446 | 282 (best known) | 282 | 368 | no | 5 / 5 | matched | |
| socfb-trinity100 | 2613 | 499 (best known) | 499 | 682 | no | 5 / 5 | matched | |
| sorrell4 | 2048 | 24 (optimal) | 24 | 66 | no | 5 / 5 | matched | |
| sorrell7 | 2048 | 198 (best known) | 198 | 366 | no | 5 / 5 | matched | |

## Method

A stable set is found as the complement of a vertex cover; no MIP or QUBO model (program `src/qob_numvc.c` in the
repository above).

- Upper bound, computed in every run: a greedy clique cover. Repeatedly take the uncovered vertex with the fewest
  uncovered neighbours and grow a clique from it among uncovered vertices, always adding the candidate adjacent to the
  most other candidates. A stable set holds at most one vertex of each clique, so the number of cliques bounds it from
  above. This is a general technique for any graph, not tied to the frb construction; on the frb instances it finds
  their clique partition. It takes under half a second on every instance.
- Search, after NuMVC (Cai, Su, Luo and Sattar, "NuMVC: an efficient local search algorithm for minimum vertex
  cover", JAIR 46, 2013). Start from a greedy cover (a random uncovered edge gets its endpoint with the larger
  score), then drop redundant vertices. Whenever the current set C covers every edge it is recorded, and the vertex of
  C with the highest score is removed, so the search then looks for a cover one vertex smaller. Each step removes the
  vertex u of C with the highest score (oldest on ties; never the vertex added in the step before), then picks a
  random uncovered edge and adds the endpoint whose configuration changed since it last left C (configuration
  checking), the higher score first, the older one on ties. Scores use edge weights: each step adds 1 to the weight of
  every uncovered edge; when the mean weight reaches gamma = n/2 every weight becomes floor(0.3 * w) (at least 1) and
  the scores are rebuilt.
- A run stops as soon as its stable set reaches the upper bound (proven optimal), or when its CPU time reaches the
  budget.

## Run protocol

- All instances: seeds 1 to 5, budget 30 s of CPU time per run.
- frb59-26-2 and frb100-40, longer runs. These were made first, with earlier builds of the same search that had no
  bound, a wall-clock limit and CPU readings only in their logs. frb59-26-2: seeds 2 to 5, 1800 s wall limits (they
  were also set by hand to stop at 59, which none of them reached).
  frb100-40: seeds 2 to 5 with 3600 s and seeds 6 and 7 with 7200 s wall limits. Their times here are the CPU readings
  in their logs. The first runs of seed 1 on both instances recorded no CPU time at all, so seed 1 was rerun with the
  current build: the same seed and the same search, so the same path. For frb59-26-2 the budget was 3600 s of CPU and
  the rerun stopped at the bound 59. For frb100-40 the budget was 1680 s of CPU, about the CPU time a 3600 s wall run
  got; it ended at that budget. These reruns are the seed-1 runs reported.
- Each instance's objective time series file holds all its runs in the order of the CSV rows (30-second runs, seeds
  1 to 5, then the longer runs in seed order): the first set, every improvement and the end of the run. The earlier
  builds wrote no time-series file, so their series were rebuilt from their logs. The logs record every new best set
  with its CPU time, except the greedy start (within the first 0.1 s), which has only a wall-clock reading. The
  solution file is the set of the first run that reached the best size.

## Timing: runtimes without waiting

Every run is a single-threaded process. The runs shared an 18-core Mac with other jobs (load about 70 to 150) at
nice 10, so the wall clock also counted time a process spent waiting for a free core. Every time reported here is
therefore the process's own CPU time (user plus system), which is the time the run takes when it has a core to
itself and excludes all waiting. Total Runtime, Time to Solution and CPU Runtime in the CSV files and the times in
the objective time series are all CPU times. Total Runtime equals CPU Runtime, since nothing else ran for the method.

## Optimality Bound

The Optimality Bound in every CSV is the clique-cover upper bound computed by the method, as described above. Where
the best set reaches it, the result is proven optimal by the run itself; the table shows which. On frb59-26-2 the
bound is 59, so the 59 found there is proven optimal. On frb100-40 the bound is 100, and our best is 97.

## Verification

Every stable set that was saved was re-checked by `check/check.py` in the repository above: each run's best set from
the current build, and the sets of the earlier longer runs that reached the listed value or beyond. It is a program
written separately from the search (Python): every index in range, no repeats, and no edge of the instance with both
endpoints in the set.

## Hardware and software

Apple M5 Pro (18 cores: 6 performance, 12 efficiency), 24 GB RAM, macOS 26.6.2. Search in C, compiled with
Apple clang 21.0.0 at -O3, one single-threaded process per run. Checker: Python 3.9.6.

## AI disclosure

generated: the search program (C), the checking program (Python) and this write-up were written with Claude
(Anthropic), model Claude Opus 5.5 (claude-opus-5-5), in Claude Code, and reviewed by the submitter, who takes
responsibility for the submission. Every solution was checked by the independent program described above. The
pull request was opened by the submitter.
