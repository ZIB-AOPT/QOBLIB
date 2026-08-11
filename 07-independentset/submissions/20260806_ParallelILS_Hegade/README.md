# Cooperative parallel ILS for Maximum Independent Set — all 50 instances

**Submitter:** Narendra N. Hegade — Kipu Quantum   **Date:** 2026-08-06

A classical solver covering all `07-independentset` instances using
**cooperative parallel iterated local search**, a multi-core metaheuristic.
Each instance is run for 10 independent trials; a trial counts as successful if it reaches the
reported objective. Runtimes are wall-clock, averaged over the trials. Every reported solution
is a verified independent set.

**Hardware:** Apple M5 Max (arm64, 48 GB RAM), 18 CPU cores; C++ solver, `clang -O3 -march=native`.

## Results

| Instance | Nodes | Objective | Best-known | Successful runs | Total Runtime (s) | vs best-known |
| :--- | ---: | ---: | ---: | :---: | ---: | :--- |
| farm | 17 | 10 | 10 | 10/10 | 0.0004 | Best-known |
| mammalia-kangaroo-interactions | 17 | 4 | 4 | 10/10 | 0.0004 | Best-known |
| johnson8-2-4 | 28 | 7 | 7 | 10/10 | 0.0003 | Best-known |
| ibm32 | 32 | 13 | 13 | 10/10 | 0.0003 | Best-known |
| karate | 34 | 20 | 20 | 10/10 | 0.0003 | Best-known |
| football | 35 | 16 | 16 | 10/10 | 0.0003 | Best-known |
| chesapeake | 39 | 17 | 17 | 10/10 | 0.0003 | Best-known |
| MANN-a9 | 45 | 3 | 3 | 10/10 | 0.0006 | Best-known |
| aves-sparrow-social | 52 | 13 | 13 | 10/10 | 0.0003 | Best-known |
| insecta-ant-colony1-day38 | 56 | 6 | 6 | 10/10 | 0.0004 | Best-known |
| hamming6-2 | 64 | 2 | 2 | 10/10 | 0.0004 | Best-known |
| hamming6-4 | 64 | 12 | 12 | 10/10 | 0.0004 | Best-known |
| sloane_1dc_64 | 64 | 10 | 10 | 10/10 | 0.0004 | Best-known |
| johnson8-4-4 | 70 | 5 | 5 | 10/10 | 0.0004 | Best-known |
| es60fst03 | 113 | 55 | 55 | 10/10 | 0.0004 | Best-known |
| johnson16-2-4 | 120 | 15 | 15 | 10/10 | 0.0007 | Best-known |
| es60fst01 | 123 | 60 | 60 | 10/10 | 0.0004 | Best-known |
| C125-9 | 125 | 34 | 34 | 10/10 | 0.0004 | Best-known |
| sloane_2dc_128 | 128 | 5 | 5 | 10/10 | 0.0010 | Best-known |
| sloane_1zc_128 | 128 | 18 | 18 | 10/10 | 0.0005 | Best-known |
| sloane_1dc_128 | 128 | 16 | 16 | 10/10 | 0.0005 | Best-known |
| insecta-ant-colony3-day09 | 160 | 9 | 9 | 10/10 | 0.0008 | Best-known |
| es60fst04 | 162 | 78 | 78 | 10/10 | 0.0011 | Best-known |
| keller4 | 171 | 11 | 11 | 10/10 | 0.0008 | Best-known |
| es60fst02 | 186 | 88 | 88 | 10/10 | 0.0006 | Best-known |
| brock200-1 | 200 | 6 | 6 | 10/10 | 0.0011 | Best-known |
| c-fat200-1 | 200 | 18 | 18 | 10/10 | 0.0004 | Best-known |
| gen200_p0-9_44 | 200 | 44 | 44 | 10/10 | 0.0009 | Best-known |
| brock200-2 | 200 | 12 | 12 | 10/10 | 0.0042 | Best-known |
| brock200-3 | 200 | 9 | 9 | 10/10 | 0.0009 | Best-known |
| brock200-4 | 200 | 8 | 8 | 10/10 | 0.0012 | Best-known |
| brock400-1 | 400 | 27 | 27 | 10/10 | 10.0100 | Best-known |
| R_500_005_1 | 500 | 91 | 91 | 10/10 | 60.0100 | Best-known |
| C500-9 | 500 | 57 | 57 | 10/10 | 5.0100 | Best-known |
| brock800-1 | 800 | 23 | 23 | 7/10 | 120.0500 | Best-known |
| frb45-21-3 | 945 | 45 | 45 | 10/10 | 30.0100 | Best-known |
| R_1000_005_1 | 1000 | 117 | 117 | 9/10 | 120.0100 | Best-known |
| hamming10-4 | 1024 | 40 | 40 | 10/10 | 5.0100 | Best-known |
| frb50-23-3 | 1150 | 50 | 50 | 9/10 | 120.0200 | Best-known |
| frb53-24-1 | 1272 | 53 | 52 | 3/10 | 120.0000 | New best-known |
| socfb-haverford76 | 1446 | 282 | 282 | 10/10 | 5.0100 | Best-known |
| p_hat1500-3 | 1500 | 94 | 94 | 10/10 | 5.0300 | Best-known |
| p_hat1500-1 | 1500 | 12 | 12 | 10/10 | 5.0700 | Best-known |
| frb59-26-2 | 1534 | 58 | 58 | 10/10 | 30.0200 | Best-known |
| sorrell7 | 2048 | 198 | 198 | 10/10 | 120.0200 | Best-known |
| sorrell4 | 2048 | 24 | 24 | 10/10 | 5.0600 | Best-known |
| socfb-trinity100 | 2613 | 499 | 499 | 10/10 | 5.0200 | Best-known |
| keller6 | 3361 | 59 | 59 | 9/10 | 60.1000 | Best-known |
| frb100-40 | 4000 | 96 | 94 | 10/10 | 5.0600 | New best-known |
| C4000-5 | 4000 | 18 | 18 | 10/10 | 12.3500 | Best-known |

All 50 instances reach the repository best-known or better, with **2 new best-known** results: frb53-24-1 (53 > 52) and frb100-40 (96 > 94).

## Reference

D. V. Andrade, M. G. C. Resende, R. F. Werneck, [*Fast local search for the maximum independent set problem*](https://doi.org/10.1007/s10732-012-9196-4), Journal of Heuristics 18 (2012) 525–547.
