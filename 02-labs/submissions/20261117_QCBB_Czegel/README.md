# QCBB with fixed-angle QAOA — Low Autocorrelation Binary Sequences (QOBLIB 02)

Submitter: András Czégel (Bentax Plus). Date: 2026-11-17. Hardware: Apple MacBook Pro, M4 Pro (8 performance + 4 efficiency cores), 24 GB RAM.

## Runs

5 independent runs with the seeds 1, 2, 3, 4, 5, one process each, one instance at a time and no
time limit. Every run of every instance labs002-labs030 ended with a proof of
optimality: its sequence has the QOBLIB optimal energy and its certified lower bound equals that
energy. Each instance reports the lowest energy over the runs, the largest certified lower bound
over the runs and the number of runs that reached this energy (`# Successful Runs`, with ε = 0).
The total runtime of a run is the wall-clock time of the whole solve, from its start to the
proof, and its time to solution is the wall-clock time until it first held a sequence of its
final energy. The CPU runtime is the measured CPU time of all threads of the process. Total
runtime, time to solution and CPU runtime are means over the runs; the remarks of each instance
give the value of every run with the median and the standard deviation. The objective time series
gives the incumbent of every run against wall-clock time, ending at the end of the run. Every
optimality bound comes from these runs. Software: macOS 27.0.1, Python 3.13.7, NumPy 2.5.4, Numba 0.68.1.

All QAOA circuits are executed by an exact noiseless statevector emulation on the CPU
(`Paradigm` = Quantum Simulator); no quantum hardware was used, so the GPU and QPU runtimes are
0. Each run gives one solution file: `solutions/<instance>_solution_<N>.sol` is the sequence of
the run with the (N+1)-th seed of the list above, with 1 for +1 and 0 for -1.

## Certificates

Each instance folder has the certificate of its optimality bound, `<instance>_certificate.json`.
A certificate records the proof that no sequence of length `n` has energy below `bound`, and how
to repeat it:

- Every LABS energy of length n lies on the lattice `bound` + `lattice_step` · Z, with
  `lattice_step` 4 or 8 depending on n, so it suffices that no sequence has energy at most
  `threshold` = `bound` − `lattice_step`.
- The branch and bound evaluated nodes until no open node had a lower bound at most
  `threshold`. The children of a node partition its completions, and every node bound is a valid
  lower bound on the energy of every completion, so the closed search tree covers all sequences.
- This holds for every sampler: the samples enter only as incumbents, whose energies are
  recomputed exactly, and in the choice of the branching spin, never in a bound or a prune.

`runs` lists, for every run, its seed, its certified lower bound, the nodes it evaluated and the
command that repeats it with the solver code. A run with a given seed evaluates the
same search tree on every repetition; the proof can also be repeated with any other sampler, for
example `--sampler sa`. Definitions and proofs are in the accompanying article.

## Method

An exact quantum-classical branch and bound built on QCBB (arXiv:2511.19501), on the native
quartic LABS Hamiltonian without quadratization or penalty terms. A best-first loop takes the open
node with the lowest bound. At every node the spins fixed so far are reduced by a symmetry rule
and by propagation, the node is bounded classically, and its Hamiltonian, the LABS energy with
the fixed spins substituted, is sampled with fixed-angle QAOA: depth p=12 with the published
fixed angles rescaled per node, no variational loop, 1,000 shots per node, at most 26 qubits
(only the root at n = 27-30 is larger; it is split into its symmetry classes without being
sampled, and every other node is sampled); for odd n the root also samples the skew-symmetric
restriction. The samples supply the incumbents and the choice between the two
outermost free spins for branching. Symmetry classes are formed from 7 boundary spins at each end
(fewer for n < 14). A run ends when no open node can improve the incumbent, which proves the
incumbent optimal. Source code: Python with Numba, available from Bentax Plus on reasonable
request under the MIT license. Reference: N/A.

## AI disclosure

assisted — AI assisted in coding and in formulating the manuscript. Claude Code (Anthropic) with the model Claude Opus 5.5 assisted in writing the Python code, the experiment scripts and the text, and Claude Fable 5.1 assisted in challenging ideas and in verifying them. The author directed the work, checked the code, the proofs and the results, and is responsible for the content.

## Results (29 instances)

| Instance | n | energy (this work) | optimality bound | proven optimal | runs with energy | mean energy | time to solution [s] | total runtime [s] | median nodes |
|---|---|---|---|---|---|---|---|---|---|
| labs002 | 2 | 1 | 1 | yes | 5/5 | 1.0 | 0.000 | 0.000 | 1 |
| labs003 | 3 | 1 | 1 | yes | 5/5 | 1.0 | 0.001 | 0.001 | 1 |
| labs004 | 4 | 2 | 2 | yes | 5/5 | 2.0 | 0.000 | 0.000 | 1 |
| labs005 | 5 | 2 | 2 | yes | 5/5 | 2.0 | 0.002 | 0.002 | 1 |
| labs006 | 6 | 7 | 7 | yes | 5/5 | 7.0 | 0.001 | 0.001 | 1 |
| labs007 | 7 | 3 | 3 | yes | 5/5 | 3.0 | 0.002 | 0.002 | 1 |
| labs008 | 8 | 8 | 8 | yes | 5/5 | 8.0 | 0.001 | 0.001 | 1 |
| labs009 | 9 | 12 | 12 | yes | 5/5 | 12.0 | 0.003 | 0.003 | 6 |
| labs010 | 10 | 13 | 13 | yes | 5/5 | 13.0 | 0.001 | 0.001 | 1 |
| labs011 | 11 | 5 | 5 | yes | 5/5 | 5.0 | 0.004 | 0.004 | 1 |
| labs012 | 12 | 10 | 10 | yes | 5/5 | 10.0 | 0.009 | 0.009 | 1 |
| labs013 | 13 | 6 | 6 | yes | 5/5 | 6.0 | 0.006 | 0.006 | 1 |
| labs014 | 14 | 19 | 19 | yes | 5/5 | 19.0 | 0.005 | 0.005 | 1 |
| labs015 | 15 | 15 | 15 | yes | 5/5 | 15.0 | 0.039 | 0.040 | 3 |
| labs016 | 16 | 24 | 24 | yes | 5/5 | 24.0 | 0.054 | 0.055 | 61 |
| labs017 | 17 | 32 | 32 | yes | 5/5 | 32.0 | 0.060 | 0.069 | 319 |
| labs018 | 18 | 25 | 25 | yes | 5/5 | 25.0 | 0.041 | 0.041 | 1 |
| labs019 | 19 | 29 | 29 | yes | 5/5 | 29.0 | 0.086 | 0.140 | 411 |
| labs020 | 20 | 26 | 26 | yes | 5/5 | 26.0 | 0.115 | 0.224 | 328 |
| labs021 | 21 | 26 | 26 | yes | 5/5 | 26.0 | 0.186 | 0.311 | 381 |
| labs022 | 22 | 39 | 39 | yes | 5/5 | 39.0 | 0.317 | 1.112 | 1777 |
| labs023 | 23 | 47 | 47 | yes | 5/5 | 47.0 | 0.610 | 8.785 | 14604 |
| labs024 | 24 | 36 | 36 | yes | 5/5 | 36.0 | 1.197 | 4.666 | 4643 |
| labs025 | 25 | 36 | 36 | yes | 5/5 | 36.0 | 4.962 | 8.910 | 6141 |
| labs026 | 26 | 45 | 45 | yes | 5/5 | 45.0 | 5.078 | 10.854 | 7080 |
| labs027 | 27 | 37 | 37 | yes | 5/5 | 37.0 | 0.035 | 13.335 | 12433 |
| labs028 | 28 | 50 | 50 | yes | 5/5 | 50.0 | 24.346 | 132.266 | 134199 |
| labs029 | 29 | 62 | 62 | yes | 5/5 | 62.0 | 0.040 | 452.110 | 443142 |
| labs030 | 30 | 59 | 59 | yes | 5/5 | 59.0 | 108.043 | 234.741 | 182730 |
