# PDBO Binary-Domain LABS Submission

This submission reports five independent stochastic PDBO runs for each QOBLIB LABS instance, using seeds 0, 1, 2, 3, and 4.

References:

- Paper: https://arxiv.org/pdf/2509.21064
- Code: https://github.com/liuwb17/PDBO

### Model

The LABS problem is naturally defined over spin variables:

$$
s_i \in \{-1, 1\}
$$

$$
C_k(s) = \sum_{i=1}^{n-k} s_i s_{i+k}
$$

LABS minimizes the following objective:

$$
E(s) = \sum_{k=1}^{n-1} C_k(s)^2
$$

The decision variables to be optimized are the binary variables $x\in\{0,1\}^n$, through the spin transform:

$$
s_i = 2x_i - 1
$$

In summary, PDBO adopts the following formulation of LABS:

$$
\underset{x\in\{0,1\}^n}{\min}\;\sum\limits_{k=1}^{n-1}\left(\sum\limits_{i=1}^{n-k}(2x_i-1)(2x_{i+k}-1)\right)^2
$$


### Runtime and Parallelism

Each instance is reported with `# Runs = 5`. Each run uses a JAX batch size of 1000, meaning that 1000 primal candidates are optimized in parallel inside one GPU execution for the same instance. These batched candidates are not counted as independent runs; the independent runs are the five seed runs.

`Total Runtime` and `GPU Runtime` are reported as averages across the five runs. `Time to Solution` is not averaged; it is the earliest timestamp among the five independent runs at which the reported best objective value is reached.

For instances with known optimal values up to `labs040`, `# Successful Runs` counts how many of the five runs reached the certified optimum. For `labs041` through `labs100`, `# Successful Runs = 0` because no proven optimal solution is available, so we do not claim that a run reached a true optimum.

### Hyperparameters

- `primal_init=uniform`
- `dual_init=100.0`
- `primal_lr=0.03`
- `dual_lr=0.03`
- `batch_size=1000`
- `seeds=0,1,2,3,4`
- `optimizer=rmsprop`

Hardware and software used for the reported runs:

- GPU: NVIDIA GeForce RTX 3090 24GB
- NVIDIA driver: 575.57.08
- CUDA: 12.9
- JAX: 0.6.1
- jaxlib: 0.6.1
