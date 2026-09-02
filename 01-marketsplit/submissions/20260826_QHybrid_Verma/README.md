# Market Split — quantum-hardware submission

Submission by Dhriti Verma, Kalyan Dasgupta, Dzung Phan, Jayant Kalagnanam (IBM).

16 instances, all solved to feasibility (`Ax = b` exactly, violation 0).
All quantum read-outs were taken on real quantum hardware: `ibm_aachen` (IBM Heron r3, 156 qubits).

## Approach

Lattice-based pre-conditioning, followed by a variational quantum sampling circuit, with classical
post-processing.

## Results

| Instance | n | Runs | Feasible | Successful | Total (s) | CPU (s) | QPU (s) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ms_07_200_248 | 60 | 5 | 5 | 5 | 209.61 | 139.07 | 70.54 |
| ms_07_200_370 | 60 | 5 | 5 | 5 | 209.51 | 138.87 | 70.64 |
| ms_07_200_398 | 60 | 5 | 5 | 5 | 207.08 | 136.72 | 70.36 |
| ms_07_200_500 | 60 | 5 | 5 | 5 | 208.84 | 138.56 | 70.28 |
| ms_08_200_000 | 70 | 5 | 5 | 5 | 227.55 | 157.45 | 70.1 |
| ms_08_200_001 | 70 | 5 | 4 | 4 | 231.52 | 161.28 | 70.24 |
| ms_08_200_002 | 70 | 5 | 5 | 5 | 229.88 | 159.86 | 70.02 |
| ms_08_200_003 | 70 | 5 | 5 | 5 | 230.54 | 160.42 | 70.12 |
| ms_09_200_000 | 80 | 5 | 5 | 5 | 217.42 | 147.35 | 70.07 |
| ms_09_200_001 | 80 | 5 | 2 | 2 | 171.27 | 98.62 | 72.65 |
| ms_09_200_002 | 80 | 5 | 5 | 5 | 109.29 | 39.04 | 70.25 |
| ms_09_200_003 | 80 | 5 | 1 | 1 | 90.84 | 21.14 | 69.7 |
| ms_10_200_000 | 90 | 5 | 4 | 4 | 299.53 | 228.82 | 70.71 |
| ms_10_200_001 | 90 | 5 | 3 | 3 | 243.97 | 131.14 | 112.83 |
| ms_10_200_002 | 90 | 5 | 5 | 5 | 138.36 | 67.55 | 70.81 |
| ms_10_200_003 | 90 | 5 | 1 | 1 | 316.46 | 203.88 | 112.58 |

## Runtime accounting

Runtimes follow the QOBLIB definition: Qiskit Runtime session mode, queue time excluded, and
inter-job idle attributed to classical runtime. `QPU Runtime` is the session-active execution time,
not the IBM-reported `actual usage` figure; the latter is quoted per instance in each `Remarks` field.
All reported runtimes are averages across the successful runs of each instance, and exclude
hyperparameter and basis-search time.

## Hardware

- Quantum: `ibm_aachen` — IBM Heron r3, 156 qubits.
- Classical: Apple M4 Max, 16 cores, 64 GB RAM, macOS 15.7.4; Python 3.14.3, Qiskit 2.4.2,
  qiskit-ibm-runtime 0.47.0, fpylll 0.6.4.

