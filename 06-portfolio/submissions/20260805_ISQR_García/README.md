# ISQR portfolio submission — shared details

Submitted by Global Data Quantum (Danel Arias, Manuel Martín Cordero, Daniel García, Álvaro Nodar).

Covers instances `po_a003_t02_orig`, `po_a004_t04_orig`, `po_a005_t04_orig`, all solved
with ISQR, a classical post-processing routine that adapts the SQD Configuration Recovery
subroutine to QUBO problems ([I. de León et al., arXiv:2512.22001, 2025](https://arxiv.org/abs/2512.22001)).

## Model, risk factor, and penalty

The QUBO follows the formulation in [`06-portfolio/info/model_setting.pdf`](../../info/model_setting.pdf).
In that document the risk tolerance is `q` (the risk factor: higher q = more risk-averse) and
`P` is the constraint penalty enforcing the capital and asset-count limits. Our implementation
denotes the risk factor `λ`.

| Instance          | Risk factor λ | Constraint penalty P |
| ----------------- | ------------- | -------------------- |
| po_a003_t02_orig  | 1e-05         | 5.0                  |
| po_a004_t04_orig  | 2e-05         | 1.0                  |
| po_a005_t04_orig  | 4e-05         | 0.5                  |

## ISQR hyperparameters

| Hyperparameter                | Value | Description |
| ----------------------------- | ----- | ----------- |
| n_shots                       | ---   | Uniform-random bitstrings sampled per seed before ISQR post-processing |
| isqr_n_batches (M)            | 100   | Configuration Recovery batches sampled per CR iteration |
| isqr_samples_per_batch        | 1000  | Bitstrings resampled (with replacement) from the counts distribution per batch |
| isqr_iterations               | 10    | Maximum number of Configuration Recovery (CR) refinement iterations |
| isqr_tol                      | 0.05  | CR stops early if the relative change in cost between iterations falls below this |
| isqr_eps                      | 0.01  | Filling-factor / leaky-ReLU threshold of the CR bit-flip probability function |

`n_shots` is the only ISQR setting that varies by instance:

| Instance          | n_shots |
| ----------------- | ------- |
| po_a003_t02_orig  | 25,000  |
| po_a004_t04_orig  | 100,000 |
| po_a005_t04_orig  | 100,000 |


## Variable mapping

For each time period `t`, variables form four consecutive blocks: **long** (`kn` vars),
**short** (`kn` vars), **asset-limit** slack (`Nb` vars), **capital-limit** slack (`Nc` vars).

At fixed `t`, the local index is `variable_id_local(d, r, a) = d·(k·n) + r·n + a`, where
`d ∈ {0,1}` is direction (0=long, 1=short), `r ∈ {0,…,k−1}` is the share-copy index, and
`a ∈ {0,…,n−1}` is the asset index. The global index adds the per-period offset:
`variable_id = t·(2kn + Nb + Nc) + variable_id_local`. Slack variables are
`asset_limit = t·(2kn + Nb + Nc) + 2kn + b` and
`capital_limit = t·(2kn + Nb + Nc) + 2kn + Nb + c`.