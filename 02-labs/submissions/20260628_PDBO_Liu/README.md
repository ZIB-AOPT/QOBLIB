# PDBO LABS Results

This submission contains PDBO results for `labs002` through `labs100`.

We solve the LABS problem directly as a polynomial unconstrained binary optimization (PUBO) problem.

### Model

For a binary sequence `x_i in {0, 1}`, define the corresponding spins

```text
s_i = 2 x_i - 1.
```

For sequence length `n`, the autocorrelations are

```text
C_k = sum_{i=1}^{n-k} s_i s_{i+k},  k = 1, ..., n-1.
```

The LABS objective minimized in this submission is the original higher-order unconstrained binary objective

```text
minimize  E(S) = sum_{k=1}^{n-1} C_k^2.
```

### Reference:

- Paper: https://arxiv.org/pdf/2509.21064
- Code: https://github.com/liuwb17/PDBO

### Hyperparameters

The runs use batch size 1000, corresponding to 1000 parallel PDBO starts from uniformly initialized primal variables. The primal and dual learning rates are 0.03, dual initialization is 100, the optimizer is RMSProp, the random seed is 0, and the time limit is 180 seconds. No local search or other post-processing refinement is applied. `GPU Runtime` is the time to solution (TTS).
