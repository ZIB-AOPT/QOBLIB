# 02 - Low Autocorrelation Binary Sequences (LABS)

[← Back to Main Repository](../README.md)

---

## Overview

The Low Autocorrelation Binary Sequences (LABS) problem seeks binary sequences with minimal autocorrelation properties. This problem has applications in communications, radar systems, and cryptography, where low autocorrelation is desirable to minimize signal interference.

## Problem Description

Given a sequence $\mathcal{S} = \{s_1, \ldots, s_n\}$ of spins $s_i \in \{-1,1\}$ for $i \in [n]$, we define:

**Autocorrelations:**
$$
C_k(\mathcal{S}) \coloneqq \sum_{i = 1}^{n-k} s_i s_{i+k}
$$

**Energy (Objective Function):**
$$
E(\mathcal{S}) \coloneqq \sum_{k=1}^{n-1} C_k^2(\mathcal{S})
$$

**Goal:** Find the binary sequence $\mathcal{S}$ of length $n$ that minimizes $E(\mathcal{S})$.

## Directory Contents

- **[instances/](instances/)** - Problem instances for various sequence lengths
- **[models/](models/)** - Mathematical model formulations
- **[solutions/](solutions/)** - Optimal or best-known solutions
- **[check/](check/)** - Solution verification tools
- **[misc/](misc/)** - Utility scripts and generators
- **[submissions/](submissions/)** - Community solution submissions

## References

* **Packebusch, T., Mertens, S.** (2016). [Low autocorrelation binary sequences](https://doi.org/10.48550/arXiv.1512.02475). Journal of Physics A: Mathematical and Theoretical, Vol 49, Number 16. DOI: 10.1088/1751-8113/49/16/165001
