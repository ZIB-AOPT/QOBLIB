# 06 - Portfolio Optimization

**Features:** Multi-period, Transaction Costs, Short Selling

[← Back to Main Repository](../README.md)

---

## Overview

This portfolio optimization problem extends classical Markowitz portfolio theory to include realistic financial market features: multiple time periods, transaction costs for buying/selling assets, borrowing costs for short positions, and capital constraints.

## Problem Description
We aim to find the binary decision variables $x_i \in \{0,1\}$ for each asset \(i\) that

$$
\min_{\substack{
x \in \{0,1\}^{n \times t}\\
y \in \{0,1\}^{c \times t}\\
s \in \{0,1\}^{b \times t}
}} 
\sum_{t=1}^{T} \biggl(
\lambda \underbrace{\sum_{i,j} \tau_{i} p_{it} x_{it} \sigma_{ijt} \tau_{j} x_{jt} p_{jt}}_{\text{risk}} - \sum_i \bigl(\underbrace{\tau_{i}(p_{it+1} - p_{it}) x_{it}}_{\text{profit}} - \underbrace{\delta p_{it} (x_{it-1} + x_{it} - 2 x_{it-1} x_{it})}_{\text{transaction cost}}\bigr) - \underbrace{\rho_c u \sum_c 2^c y_{ct}}_{\text{cash interest}} + \underbrace{\rho_s \sum_{i \in S} p_{it} x_{it}}_{\text{short selling cost}}\biggr) + \underbrace{\delta \sum_i p_{iT} x_{iT}}_{\text{liquidation cost}}
$$

subject to the constraints:

$$
\sum_i \tau_i x_{it} + \sum_c 2^c y_{ct} = C \quad \forall t \in \{1,...,T\} \quad \quad {\text{capital limit}}
$$

$$
\sum_i x_{it} + \sum_b 2^b s_{bt} = B \quad \forall t \in \{1,...,T\} \quad \quad {\text{number of assets limit}}
$$

Here, $p_{i,t}$ represents the price of one unit of asset $i$ at time $t$, and $\sigma_{ij,t}$ denotes the covariance between stocks $i$ and $j$ at time $t$. We denote by $\delta$ the transaction cost rate applied to both buying and selling. We have a short-selling indicator $\tau \in \{-1, +1\}$, where $-1$ indicates a short position and $+1$ a long position. Our model includes a borrowing cost rate for short sales, denoted by $\rho_s$. We introduce slack variables $s_{bt} \in \{0,1\}$ for $b \in \{0, \ldots, \lfloor \log_2 B \rfloor\}$ to cap the total number of assets, and use slack variables $y_{ct} \in \{0,1\}$ for $c \in \{0, \ldots, \lfloor \log_2 C \rfloor\}$ to help restrict the total available cash to not exceed $C$ units.

## Directory Contents

- **[instances/](instances/)** - Portfolio optimization instances with market data
- **[models/](models/)** - Mathematical model formulations
- **[solutions/](solutions/)** - Optimal or best-known solutions
- **[check/](check/)** - Solution verification tools
- **[info/](info/)** - Additional documentation and papers
- **[misc/](misc/)** - Utility scripts and data generators
- **[submissions/](submissions/)** - Community solution submissions

## Related Works

- **Brandhofer et al.** - [Benchmarking the performance of portfolio optimization with QAOA](https://doi.org/10.1007/s11128-022-03766-5)
- **Hodson et al.** - [Portfolio rebalancing experiments using the Quantum Alternating Operator Ansatz](https://arxiv.org/abs/1911.05296)
- **Baker & Radha** - [Wasserstein Solution Quality and the Quantum Approximate Optimization Algorithm: A Portfolio Optimization Case Study](https://arxiv.org/pdf/2202.06782)
- **Mugel et al.** - [Dynamic Portfolio Optimization with Real Datasets Using Quantum Processors and Quantum-Inspired Tensor Networks](https://doi.org/10.1103/PhysRevResearch.4.013006)
- **Herman et al.** - [Constrained optimization via quantum Zeno dynamics](https://doi.org/10.1038/s42005-023-01331-9)
- **Giron et al.** - [Approaching Collateral Optimization for NISQ and Quantum-Inspired Computing](https://doi.org/10.1109/TQE.2023.3314839)
- **Woerner & Egger** - [Quantum risk analysis](https://doi.org/10.1038/s41534-019-0130-6)
- **Egger et al.** - [Credit Risk Analysis using Quantum Computers](https://doi.org/10.1109/TC.2020.3038063)
- **Stamatopoulos et al.** - [Option Pricing using Quantum Computers](https://doi.org/10.22331/q-2020-07-06-291)
- **Braine et al.** - [Quantum algorithms for mixed binary optimization applied to transaction settlement](https://doi.org/10.1109/TQE.2021.3063635)
- **Calude et al.** - [QUBO formulations for the graph isomorphism problem and related problems](http://dx.doi.org/10.1016/j.tcs.2017.04.016)
- **Becker, Cheridito, Jentzen** - [Deep optimal stopping](https://doi.org/10.3929/ethz-b-000344707)
- **Felizardo, Matsumoto, Del-Moral-Hernandez** - [Solving the optimal stopping problem with reinforcement learning](https://doi.org/10.1109/IJCNN55064.2022.9892333)
- **Soon & Ye** - [Currency Arbitrage Detection Using A Binary Integer Programming Model](https://doi.org/10.1109/IEEM.2007.4419314)
- **Díez-Valle et al.** - [Multi-objective variational quantum optimization for constrained problems: an application to Cash Management](https://doi.org/10.1088/2058-9565/ace474)

## References

* **Brandhofer, S., et al.** (2022). [Benchmarking the performance of portfolio optimization with QAOA](https://link.springer.com/content/pdf/10.1007/s11128-022-03766-5.pdf). Quantum Information Processing 22.1: 25.

* **Mugel, S., et al.** (2022). [Dynamic portfolio optimization with real datasets using quantum processors and quantum-inspired tensor networks](https://journals.aps.org/prresearch/pdf/10.1103/PhysRevResearch.4.013006). Physical Review Research 4.1: 013006.