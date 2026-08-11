# QOBLIB Portfolio Optimization Solution Checker

This program is part of **QOBLIB - Quantum Optimization Benchmarking Library**
and verifies solutions to the *Multi-Period Portfolio Optimization* problem
(`06-portfolio`). It checks feasibility and recomputes the objective value of
the reference model in exact arithmetic, so that the result agrees
bit-for-bit with any solver run on the shipped LP/QUBO model files.

## Reference model

The reference model is
[`models/binary_quadratic_programming/bqp_u3_c10.zpl`](../models/binary_quadratic_programming/bqp_u3_c10.zpl)
with the parameters of
[`parameter_u3_c10.zpl`](../models/binary_quadratic_programming/parameter_u3_c10.zpl).
For each asset $i$, unit copy $m \in \{1,\dots,ub\}$, direction
$\tau \in \{+1,-1\}$ (long/short) and period $t$ there is a binary variable
$x_{i,m,\tau,t}$; one *unit* is the number of shares worth `unit` = 100 000
cash at $t=0$. Binary slack registers enforce, per period,

* capital: $\sum \tau\, x + \sum_c 2^c y_{c,t} = C$ with $C = cash/unit = 10$
  and $c \in \{0,\dots,3\}$, i.e. the net position lies in $[C-15,\, C]$;
* budget: $\sum x + \sum_b 2^b s_{b,t} = B$ with $b \in \{0,\dots,6\}$,
  i.e. the total number of open positions lies in $[B-127,\, B]$.

Only $B$ (budget, encoded as `bXXX` in model names) and $\lambda$ (risk
weight, `lX`) vary between model variants; all other parameters are fixed.

## Canonical solution format

A solution file is plain text. Everything from `#` to the end of a line is a
comment. Non-empty lines are either **header lines** (`key value`) or
**position lines**:

```
# Optimal solution found by Gurobi 11
instance po_a010_t10_orig
budget 4
lambda 0.0001
objective -69482
# period  symbol  long  short
0 AAPL  0 1
0 GOOGL 3 0
1 META  1 0
1 TSLA  0 3
```

Header keys:

| Key         | Required | Meaning |
|-------------|----------|---------|
| `instance`  | no       | Instance name (e.g. `po_a010_t10_orig`); checked against the instance directory, mismatch is a warning. |
| `budget`    | yes*     | The budget $B$ of the model variant (the `bXXX` part). |
| `lambda`    | yes*     | The risk weight $\lambda$ (the `lX` part), decimal or scientific notation. |
| `objective` | no       | Claimed objective value; if present it must match the recomputed value **exactly**. |

*may instead be supplied on the command line with `--budget` / `--lambda`,
which take precedence.

Position lines have exactly four fields:

```
<period> <symbol> <long units> <short units>
```

* `period` is 0-based and must be smaller than the number of periods of the
  instance.
* `symbol` must occur in the instance's `stock_prices` file.
* `long units` and `short units` are integers in $\{0,\dots,ub\}$ (default
  $ub = 3$): the number of unit copies held long resp. short.
* At most one line per (period, symbol); omitted pairs hold no position.

### Relation to the binary model

The format stores unit *counts* instead of individual copy variables because
the model is symmetric under permuting copy slots: coefficients do not depend
on $m$. A count vector corresponds to the canonical assignment that fills
copies $1,\dots,u$, under which the rebalancing cost between consecutive
periods is $\delta\, p_{i,t}\, |u_{i,\tau,t} - u_{i,\tau,t-1}|$ per (asset,
direction) — the minimum over all slot assignments realizing the same counts.
Optimal values of the count formulation and of the LP/QUBO files therefore
coincide. To convert a solver's bitstring, count the set variables per
(asset, direction, period); for an optimal solution the canonical objective
equals the solver's objective. (For non-optimal solutions with misaligned
copy slots the canonical value can only be better; the checker reports the
canonical value.)

Slack registers are **not** part of the format: they are uniquely determined
by the positions and are validated and priced (cash interest) by the checker.

## What the checker does

1. **Parses** the instance (`stock_prices.txt[.gz]`,
   `covariance_matrices.txt[.gz]`) and the solution file.
2. **Checks feasibility** per period: the required cash slack $C - \text{net}$
   must lie in $[0, 2^{4}-1]$ and the count slack $B - \text{total}$ in
   $[0, 2^{7}-1]$.
3. **Recomputes the objective** — risk, return, transaction cost, cash
   interest, short-selling cost and liquidation cost — in exact rational
   arithmetic. Every coefficient is rounded exactly like Zimpl's `round()`
   (round half away from zero on exact rationals), so the value is
   bit-identical to the coefficients in the shipped LP/QUBO files. The
   breakdown and the total are printed; a claimed `objective` is verified.

The recomputation has been cross-validated coefficient-for-coefficient
against Zimpl-generated LP files (all linear and quadratic coefficients) for
several instances, seeds and $\lambda$ values, and reproduces the objective
values of the optimal Gurobi reference solutions exactly.

## Usage

### Building

```bash
cargo build --release
```

### Command

```bash
./target/release/check_portfolio <instance-dir> <solution-file> [options]
```

`<instance-dir>` is the instance directory (e.g.
`../instances/po_a010_t10_orig`) or the instances root, in which case the
directory is resolved from the solution's `instance` header.

Options (defaults are the values of `parameter_u3_c10.zpl`):
`--budget B`, `--lambda L`, `--ub N` [3], `--cash V` [1000000],
`--unit V` [100000], `--delta V` [0.001], `--nu V` [0.0001],
`--rho V` [0.000025], `--cs1 N` [4], `--cs2 N` [7], `--upscale V` [1].

### Example

```
$ ./target/release/check_portfolio ../instances/po_a010_t10_orig \
      ../solutions/a010_t10_orig_b004_l0.0001.bst.sol
Instance: po_a010_t10_orig (10 assets, 10 periods)
Model:    B=4, lambda=0.0001, ub=3, C=10, slack bits 4+7
t= 0: net=   2 total=   4 cash_slack=   8 count_slack=   0  ok
...
Objective breakdown:
  risk                       23416
  return                    -97869
  transaction                 5821
  cash interest               -880
  short cost                    30
  liquidation                    0
Objective value = -69482
Claimed objective matches.
Solution successfully verified
```

### Checking all curated solutions

```bash
sh check_all.sh
```

## Exit codes

Per [`misc/ci/CHECKER_CONTRACT.md`](../../misc/ci/CHECKER_CONTRACT.md):

| Code | Meaning |
|------|---------|
| `0`  | Solution file is valid and feasible. |
| `21` | Well-formed but violates the capital or budget constraint. |
| `10` | Invalid file: malformed line, unknown symbol, period out of range, unit count above `ub`, duplicate entry, or a claimed `objective` that does not match the recomputed value. |
| `2`  | Bad command-line arguments or unreadable instance files. |

The checker does not know optimal values and therefore never returns `20`.

## Converting existing solver output

[`../misc/lp_sol_to_canonical.py`](../misc/lp_sol_to_canonical.py) converts a
solver solution for one of the shipped portfolio models into the canonical
format. It auto-detects three input formats from the solution file:

| Format | Variable names | Model reference argument | Used by |
|--------|----------------|--------------------------|---------|
| `bqp-lp` | Zimpl-mangled LP names (`x$GOOGL#1#_1#0@fa`, `y#0#0`) | the **LP file** (`.lp[.xz\|.gz]`) | Gurobi `.sol` for a shipped BQP LP file; `solutions/bqp/*` |
| `uqo-index` | flat positional index (`x#1` … `x#710`) | the **instance directory** | UQO `.qs` solutions; `solutions/uqo/*` |
| `bitstring` | one 0/1 per line, in `uqo-index` order | the **instance directory** | QUBO samplers emitting a raw bitstring of model length |

```bash
python3 ../misc/lp_sol_to_canonical.py \
    <lp-file[.xz|.gz] | instance-dir> <solver.sol> \
    <instance-name> <budget> <lambda> [out.sol] [--ub N]
```

* For `bqp-lp` the LP file is required because Zimpl truncates long variable
  names and appends a unique `@<hex>` suffix; the `c2` constraint rows are used
  to resolve the ambiguity. Any λ variant of the instance's LP works — only the
  variable names, not the objective, are read from it.
* For `uqo-index` / `bitstring` the flat variable order is reconstructed
  analytically from the instance's `stock_prices` file: Zimpl creates
  `var x[SX*TX]` as `asset (file order) → copy m (1..ub) → direction τ (+1,-1)
  → period t (0..T-1)`, followed by the slack registers `y[CS1×TX]` and
  `s2[CS2×TX]`. Only the `x` variables are used; the slacks are recomputed by
  the checker.
* The reported `objective` is rounded to the nearest integer. The reference
  objective is provably integer (every coefficient is a Zimpl `round(...)` and
  all variables are binary), so this removes the solver's float noise (e.g.
  `-31504.0140…` → `-31504`) that the exact-arithmetic checker would otherwise
  reject.

Not every solution maps to a shipped model: a raw bitstring whose length does
not equal the model's variable count (e.g. a reduced-qubit / compressed
encoding such as Arvak's PCE model) is rejected with an explanatory error
rather than silently mis-decoded.

## CI integration

The portfolio checker is wired into the automatic submission validator at
`misc/ci/check_submission.py::_build_auto_checker_cmd`. Submissions must be in
the canonical format (convert solver output with the tool above first); the
concrete instance directory is resolved from each solution's `instance`
header, and the budget/λ are read from the solution's own header:

```python
if prob.startswith("06-"):
    binary = _ensure_checker_built(check_dir, "check_portfolio")
    if not binary:
        return None
    return [str(binary), str(instances_dir), str(solution)]
```

Exit codes are interpreted against the submission's `*_summary.csv` claims per
[`../../misc/ci/CHECKER_CONTRACT.md`](../../misc/ci/CHECKER_CONTRACT.md): a
valid, feasible file passes; a well-formed but infeasible file (exit `21`) is
accepted only when the submission does **not** claim feasibility (e.g. penalty
QUBO / UQO solutions that legitimately violate the hard constraints).

## License

Part of **QOBLIB**, released under
[**Apache 2.0**](http://www.apache.org/licenses/LICENSE-2.0).

## Author

**Maximilian Schicker**
© 2026
