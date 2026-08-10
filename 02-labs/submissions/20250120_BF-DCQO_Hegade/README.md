# BF-DCQO Quantum Baseline for LABS

Results from solving the low autocorrelation binary sequences (LABS) problem at sequence length $N = 20$ with BF-DCQO on IBM quantum hardware.

Reference: https://github.com/AlejoKQ/data_LABS_BF-DCQO_Benchmark

### Results

Ten independent runs were executed. All ten reached $E = 26$, which matches the proven
optimum for $N = 20$; the submission does not claim a proven bound, since BF-DCQO
derives none of its own.

| Run | Iterations | QPU [s] | Pre-proc. [s] | Post-proc. [s] | Total [s] | Ground-state prob. |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1  | 1 | 32  | 0.213 | 0.01 | 32.23  | 0.10 |
| 2  | 1 | 32  | 0.241 | 0.01 | 32.25  | 0.23 |
| 3  | 1 | 32  | 0.216 | 0.01 | 32.23  | 0.37 |
| 4  | 1 | 32  | 0.226 | 0.01 | 32.24  | 0.45 |
| 5  | 1 | 32  | 0.225 | 0.01 | 32.24  | 0.10 |
| 6  | 3 | 96  | 0.665 | 0.01 | 96.68  | 0.25 |
| 7  | 2 | 64  | 0.427 | 0.01 | 64.44  | 0.49 |
| 8  | 2 | 64  | 0.408 | 0.01 | 64.42  | 0.13 |
| 9  | 4 | 128 | 0.854 | 0.01 | 128.87 | 0.08 |
| 10 | 3 | 96  | 0.630 | 0.01 | 96.64  | 0.12 |
| **mean** | 1.9 | **60.8** | 0.4105 | 0.01 | **61.224** | 0.232 |

The sequence found by each run is in `labs020/solutions/`, where run $n$ of the table
corresponds to `labs020_solution_`$(n-1)$`.sol`. The ten runs produced five distinct
ground states.

`Time to Solution` is reported as `N/A` because no timestamp was recorded for when the
optimum first appeared within a run.

### Hardware and software

- CPU: Apple M2 Pro
- QPU: `ibm_marrakesh`
- Qiskit 1.3.1, NumPy 2.0.2, SciPy 1.14.1

