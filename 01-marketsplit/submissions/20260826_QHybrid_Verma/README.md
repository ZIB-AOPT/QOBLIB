# Market Split — quantum-hardware submission

Submission by Dhriti Verma, Kalyan Dasgupta, Dzung Phan, Jayant Kalagnanam (IBM).

16 instances, all solved to feasibility (`Ax = b` exactly, violation 0).
All quantum read-outs were taken on real quantum hardware: `ibm_aachen` (IBM Heron r3, 156 qubits).

## Approach

Lattice-based pre-conditioning, followed by a variational quantum sampling circuit, with classical
post-processing.

## Results

| Instance | n | Total runtime (s) | CPU (s) | QPU (s) |
| --- | --- | --- | --- | --- |
| ms_07_200_248 | 60 | 210.26 | 136.77 | 73.49 |
| ms_07_200_370 | 60 | 210.51 | 136.52 | 73.99 |
| ms_07_200_398 | 60 | 206.85 | 134.24 | 72.61 |
| ms_07_200_500 | 60 | 210.2 | 138.02 | 72.18 |
| ms_08_200_000 | 70 | 227.03 | 155.75 | 71.28 |
| ms_08_200_001 | 70 | 230.96 | 158.98 | 71.98 |
| ms_08_200_002 | 70 | 229.74 | 158.85 | 70.89 |
| ms_08_200_003 | 70 | 229.48 | 158.08 | 71.4 |
| ms_09_200_000 | 80 | 220.01 | 148.87 | 71.14 |
| ms_09_200_001 | 80 | 170.06 | 98.79 | 71.27 |
| ms_09_200_002 | 80 | 112.98 | 40.93 | 72.05 |
| ms_09_200_003 | 80 | 89.82 | 20.52 | 69.3 |
| ms_10_200_000 | 90 | 297.88 | 224.12 | 73.76 |
| ms_10_200_001 | 90 | 232.95 | 130.78 | 102.17 |
| ms_10_200_002 | 90 | 137.29 | 66.01 | 71.28 |
| ms_10_200_003 | 90 | 299.61 | 199.07 | 100.54 |

## Runtime accounting

Runtimes follow the QOBLIB definition: Qiskit Runtime session mode, queue time excluded, and
inter-job idle attributed to classical runtime. `QPU Runtime` is the session-active execution time,
not the IBM-reported `actual usage` figure; the latter is quoted per instance in each `Remarks` field.
Runtimes are for the single reported configuration per instance and exclude hyperparameter and
basis-search time. Each row is a single hardware run (`# Runs = 1`), so no run-to-run statistics are
reported.

## Hardware

- Quantum: `ibm_aachen` — IBM Heron r3, 156 qubits.
- Classical: Apple M4 Max, 16 cores, 64 GB RAM, macOS 15.7.4; Python 3.14.3, Qiskit 2.4.2,
  qiskit-ibm-runtime 0.47.0, fpylll 0.6.4.

