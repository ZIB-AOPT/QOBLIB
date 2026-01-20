# Quantum Baseline Results

The dataset contains results from solving the low autocorrelation binary optimization (LABS) problem with sequence length N=20. This problem is modeled as a Higher-order Unconstrained Binary Optimization (HUBO) problem. The problem formulation included 20 binary decision variables. The model featured 90 quadratic terms with coefficient 2 and 525 quartic terms with coefficient 4.

A stochastic algorithm was employed, specifically using sampling with the BF-DCQO algorithm combined with local search sweeps in each iteration. Ten experimental runs were conducted, all of which successfully found feasible solutions. The total runtime for these experiments was 61.22 seconds, consisting of 0.42 seconds CPU runtime and 60.80 seconds Quantum Processing Unit (QPU) runtime.

There is also a file called "bitstrings.json" which shows the optimal bitstrings found for each trial.