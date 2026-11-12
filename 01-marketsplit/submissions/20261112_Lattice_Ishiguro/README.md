# Market split via lattice sieving (1 GPU, 5 runs)

Submitter: Tsukasa Ishiguro (Toyota Motor Corporation)

## Method

Each instance `Ax = b` (x ∈ {0,1}^n) is treated as a shortest-vector problem in a lattice.

1. **Lattice embedding.** `Ax = b` is embedded into a lattice in the same way as in
   Wassermann's lattice approach, so that a solution x corresponds to a short lattice vector.
2. **Lattice reduction.** LLL, then BKZ with block size 40 (fplll / fpylll).
3. **Sieving.** G6K GPU sieve on the full rank of the lattice, which produces a large set of
   short lattice vectors. The sieve is stopped at a target saturation of 0.425 instead of the
   default, which cuts its fixed cost. Every run runs the sieve from scratch;
   no set of short vectors is reused between runs.
4. **Scan of the short vectors.** Every short vector is checked for the pattern that encodes a
   solution. For some instances the solution is already there.
5. **Search over combinations of the short vectors.** Otherwise the solution is searched for by
   combining short vectors. Starting from a vector that encodes a candidate assignment, short
   vectors are added one at a time, each step taking the one that shortens the current vector the
   most, until no short vector shortens it further. A vector of the length that a solution must
   have is a solution; otherwise the search starts again from a new random starting point. The
   search runs on the GPU (batched int8 GEMM on Tensor Cores) and is seeded.
6. **Exact check.** The recovered x is verified to satisfy `Ax = b` with exact integer arithmetic.

The algorithm is stochastic. The search in step 5 is randomized and seeded (seeds 3–7). The GPU
sieve is not seeded but is nondeterministic (multithreaded GPU execution), so its output also
differs between runs; a run is therefore not exactly reproducible from its seed. Every instance
was run 5 times independently with identical settings (seeds 3, 4, 5, 6, 7); all 5 runs found a
feasible solution in every instance.

### Hyperparameters

| Stage | Setting |
| --- | --- |
| Reduction | LLL, then BKZ block size 40 |
| Sieve | G6K GPU sieve, target saturation 0.425, no dimensions for free, up to 8 densification passes at full rank |
| Search | 512 starting points in parallel; each step adds the single short vector that shortens the current vector the most; budget 3,000,000 restarts |
| Seeds | 3, 4, 5, 6, 7 for the search in step 5 (one run each; the sieve is not seeded) |

## Hardware

- 1× NVIDIA H100 80GB HBM3 (SXM), driver 580.126.20
- 32 threads of 2× Intel Xeon Platinum 8480+ (2 × 56 cores, SMT2)
- Node: Supermicro SYS-821GE-TNHR (HGX H100 8-GPU); one GPU and 32 threads allocated per job.
  Jobs may share a node, but at most one job with m = 15 runs on a node, because the expansion of
  the largest databases is limited by memory bandwidth
- Host memory allocated per job: 48–512 GiB depending on the lattice rank

## Software

- Container base: `nvidia/cuda:12.4.1-devel-ubuntu22.04` (Ubuntu 22.04.4 LTS), Python 3.10.12
- fplll 5.4.1, fpylll 0.5.6
- G6K-GPU-Tensor (WvanWoerden), branch `python3lwe`, commit
  `e0e17ad1c131886adf9ba2f057db6f6f2670fd2d` (2022-01-10), MAXDIM = 128
- PyTorch 2.6.0 (CUDA 12.4), CuPy 14.2.0, NumPy 2.2.6

## Reported values

- **Total Runtime / Time to Solution:** mean over the 5 runs of the wall-clock time from the start
  of the sieve stage to the end of the search stage, including all stages (embedding, reduction,
  sieving, loading the database, search). The run stops as soon as a solution is found, so the two
  values are equal. Minimum and maximum over the 5 runs are given in Remarks.
- **CPU / GPU Runtime:** both equal to Total Runtime. The 32 CPU threads and the GPU are allocated
  and used concurrently throughout the run, so the time is not split between them; both fields give
  wall-clock time, not busy time.
- **Best Objective Value / Optimality Bound:** N/A (feasibility problem).
- **Solutions:** `solutions/<instance>_solution_<N>.sol` holds the distinct solutions found in the
  5 runs, one file per distinct vector (identical solutions are not repeated), numbered in order of
  the first seed that found them. Remarks lists the seeds behind each file. For D = 200 the 5 runs
  return the same vector (the solution is essentially unique), so there is one file; for D = 50
  and 100 the runs mostly return different vectors. # Feasible Runs (= 5) counts runs, not files.

## AI disclosure

assisted — the solver code was drafted with Claude (Anthropic), models Fable5.1 and Opus5.5,
then reviewed and edited by the authors.
