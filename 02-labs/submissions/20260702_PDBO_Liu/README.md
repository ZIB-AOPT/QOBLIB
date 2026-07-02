# PDBO LABS Submission

This submission reports PDBO results for the QOBLIB LABS instances.

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

Each instance is reported as one stochastic PDBO run:

- `# Runs = 1`
- `# Feasible Runs = 1`
- For `labs002` through `labs040`, `# Successful Runs = 1` if the run reached the certified optimum and `0` otherwise.
- For `labs041` through `labs100`, `# Successful Runs = 0` because no proven optimal solution is available, so we do not claim that a run reached a true optimum.

The PDBO implementation uses a JAX batch size of 1000. This means that 1000 primal candidates are optimized in parallel inside one GPU execution for the same instance. These are not 1000 independent repetitions with separate seeds, so the submission does not report them as 1000 runs.

`Total Runtime` is the wall-clock runtime of the single solver execution for the instance. `GPU Runtime` reports the same GPU wall-clock runtime, since the computation is GPU-driven. The objective time series records incumbent improvements during the run. `Time to solution` is the first timestamp at which the final reported incumbent objective value was reached.

### Hyperparameters

- `primal_init=uniform`
- `dual_init=100.0`
- `primal_lr=0.03`
- `dual_lr=0.03`
- `batch_size=1000`
- `seed=0`
- `optimizer=rmsprop`

Hardware and software used for the reported runs:

- GPU: NVIDIA GeForce RTX 3090 24GB
- NVIDIA driver: 575.57.08
- CUDA: 12.9
- JAX: 0.6.1
- jaxlib: 0.6.1

For instances with known optimal values up to `labs040`, the run used the known optimum as an early-stop cutoff. 



