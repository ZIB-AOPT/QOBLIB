# Quicopt v0.2 LABS Submission

Low-autocorrelation binary sequences for every QOBLIB LABS instance, `labs002`
through `labs100`, submitted 2026-08-15.

### Model

The sequence is a spin vector, and the objective is its sidelobe energy:

$$
s \in \{-1, 1\}^n, \qquad
C_k(s) = \sum_{i=1}^{n-k} s_i s_{i+k}, \qquad
E(s) = \sum_{k=1}^{n-1} C_k(s)^2 .
$$

Solutions are written in the repository's `0 = +1` convention. The model-size
columns describe the multilinear expansion of that objective, which has degree-2
and degree-4 terms only; at `labs100` it carries 82075 non-zero coefficients,
matching the PDBOspin entry. Note that the column headings abbreviate "number of"
as a leading `#`; that is the repository's schema, not Markdown.

### What a run is, and what it costs

A **run** is one independent execution producing one candidate sequence. Runs of
an instance share one pre-processing stage, and that stage is charged to **each
run in full**, so `Total Runtime` is the cost of one answer from cold and does
not fall as more runs are added.

The consequence is deliberate and worth stating plainly: the number of runs
times `CPU Runtime` is **larger** than the compute actually spent, because the
shared stage ran once for each group of runs and the runs ran concurrently. Every
row's `Remarks` gives the split between a run's own work and the shared stage, and
states the true total consumed for that instance. Across all 99 instances that
true total is 636 CPU-hours.

Averaging the shared stage over the runs instead would report the marginal cost
of one more candidate, which makes an instance look cheaper the more compute went
into it. That is why it is not done here.

### Reading the other columns

- `Optimality Bound` is `N/A` at every instance, including those whose optimum is
  proven in the literature. The field means the bound *this run* proved; a
  stochastic method proves none, so no optimality is claimed anywhere.
- The successful-run count is the number of runs reaching the reported objective
  at `Success Threshold = 0`. It is 1 at 46 instances, so rare-event results
  declare themselves rather than hiding inside an average.
- `Time to Solution` is the first entry in a run's objective time series reaching
  that run's final incumbent, averaged over **all** runs of the instance, not
  only successful ones.
- Objective time series are supplied at the 51 instances where every run of
  the instance has one.

### Reproducibility

Every result was regenerated end-to-end from a committed state, at the same
concurrency as the run being reported, and the reported cost is that of the run
that produced it. Reruns return the same sequences bit-for-bit.

### Hardware

AMD EPYC-Rome, 255 vCPUs, 503 GB RAM; Ubuntu 24.04.4 LTS, Linux 6.8.0, x86-64.
Runs were executed concurrently, so a run's wall-clock includes contention.
