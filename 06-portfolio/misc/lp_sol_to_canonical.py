#!/usr/bin/env python3
# This file is part of QOBLIB - Quantum Optimization Benchmarking Library
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Convert a solver solution for one of the shipped portfolio models into the
canonical QOBLIB portfolio solution format (see ../check/README.md).

Three input formats are auto-detected from the solution file:

* **bqp-lp** — Gurobi/CPLEX ``.sol`` written in the Zimpl-mangled LP variable
  names of a shipped BQP LP file (tokens like ``x$GOOGL#1#_1#0@fa`` and
  ``y#0#0``). Zimpl truncates long names and appends a unique ``@<hex>``
  suffix, so the names alone are ambiguous (the period index of e.g.
  ``x$GOOGL#1#_1#@fa`` is cut off). They are resolved through the ``c2``
  constraint rows of the LP file: each row belongs to one period, and within a
  row every mangled short variable (coefficient -1) is immediately followed by
  its untruncated long twin (coefficient +1) for the same asset and copy.
  → the model reference argument must be the **LP file**.

* **uqo-index** — a ``.sol`` in the flat, positionally indexed variable names
  of a shipped UQO ``.qs`` file (tokens like ``x#1 0`` / ``x#710 1``). The
  index is Zimpl's variable-creation order for ``var x[SX*TX]`` followed by the
  slack registers ``y`` and ``s2``, i.e.
  ``asset (stock_prices order) → copy m (1..ub) → direction τ (+1,-1) →
  period t (0..T-1)``, then ``y[CS1×TX]`` (40 vars), then ``s2[CS2×TX]``.
  → the model reference argument must be the **instance directory** (its
  ``stock_prices`` file fixes the asset order and the number of periods).

* **bitstring** — one 0/1 value per line, in the same variable order as
  ``uqo-index`` (as emitted by many QUBO samplers). The number of values must
  equal the model's variable count ``|SX|·T + |CS1|·T + |CS2|·T``.
  → the model reference argument must be the **instance directory**.

Only the ``x`` variables carry information; the slack registers (``y``,
``s2``) are recomputed and validated by the checker and are ignored here.

Usage:
    python3 lp_sol_to_canonical.py <lp[.xz|.gz] | instance-dir> <solver.sol> \
            <instance-name> <budget> <lambda> [out.sol] [--ub N] [--objective V]

    --objective V   Override or supply the claimed objective value (integer).
                    When present, the value is written to the ``objective``
                    header and the checker will verify it matches the
                    recomputed value exactly.  Use this when the solver does
                    not emit a ``# Objective value = ...`` comment (e.g. QUBO
                    samplers that report a QUBO energy rather than the
                    portfolio objective).  If the value is wrong the checker
                    exits with code 10 (INVALID_FILE).
"""
import gzip
import lzma
import os
import re
import sys
from collections import defaultdict

NAME = r"[A-Za-z0-9_$#.@]+"
TERM = re.compile(r"([+-])\s*(\d+)?\s*(" + NAME + r")")

DEFAULT_UB = 3


def opener(path):
    if path.endswith(".gz"):
        return gzip.open(path, "rt")
    if path.endswith(".xz"):
        return lzma.open(path, "rt")
    return open(path)


# --------------------------------------------------------------------------- #
# bqp-lp: resolve Zimpl-mangled names through the LP c2 constraint rows.
# --------------------------------------------------------------------------- #
def name_map_from_lp(lp_path):
    """name -> (symbol, copy, tau, period) for every x variable."""
    with opener(lp_path) as f:
        text = "\n".join(l for l in f.read().splitlines() if not l.startswith("\\"))
    m = re.search(r"Subject to\n(.*?)\n(Bounds|Binaries|Binary|General|End)", text, re.S)
    if not m:
        raise SystemExit("could not locate constraint section in LP file")
    cons = m.group(1)
    name2sem = {}
    for row in re.finditer(r"c2_(\d+):(.*?)(?=\n [a-z]|\Z)", cons, re.S):
        period = int(row.group(1)) - 1
        lhs = row.group(2).split("=")[0]
        if lhs.strip() and lhs.strip()[0] not in "+-":
            lhs = "+" + lhs
        toks = [(s, int(c) if c else 1, n) for s, c, n in TERM.findall(lhs)]
        i = 0
        while i < len(toks):
            sign, coef, name = toks[i]
            if name.startswith("y#"):
                i += 1
                continue
            if sign == "+":  # long: untruncated x$SYM#m#1#t
                mm = re.match(r"x\$(.+)#(\d+)#1#(\d+)$", name)
                if not mm:
                    raise SystemExit(f"unexpected long variable name {name}")
                name2sem[name] = (mm.group(1), int(mm.group(2)), 1, period)
                i += 1
            else:  # short (mangled); long twin follows
                _, _, twin = toks[i + 1]
                mm = re.match(r"x\$(.+)#(\d+)#1#(\d+)$", twin)
                if not mm:
                    raise SystemExit(f"unexpected pairing {name} / {twin}")
                name2sem[name] = (mm.group(1), int(mm.group(2)), -1, period)
                name2sem[twin] = (mm.group(1), int(mm.group(2)), 1, period)
                i += 2
    return name2sem


def counts_from_bqp_lp(lp_path, sol_path):
    name2sem = name_map_from_lp(lp_path)
    counts = defaultdict(lambda: [0, 0])
    objective = None
    with open(sol_path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line.startswith("#"):
                m = re.search(r"Objective value\s*=\s*(-?[\d.eE+]+)", line)
                if m:
                    objective = m.group(1)
                continue
            name, val = line.split()
            v = round(float(val))
            if v == 0:
                continue
            if name.startswith(("y#", "s2#")):
                continue
            if name not in name2sem:
                raise SystemExit(f"unmapped variable name: {name}")
            sym, _, tau, t = name2sem[name]
            counts[(t, sym)][0 if tau == 1 else 1] += v
    return counts, objective


# --------------------------------------------------------------------------- #
# uqo-index / bitstring: reconstruct Zimpl's flat variable order analytically.
# --------------------------------------------------------------------------- #
def _stock_prices_path(instance_dir):
    for name in ("stock_prices.txt.gz", "stock_prices.txt"):
        p = os.path.join(instance_dir, name)
        if os.path.exists(p):
            return p
    raise SystemExit(f"no stock_prices.txt[.gz] in {instance_dir}")


def symbols_and_periods(instance_dir):
    """Asset symbols in file order and the number of periods T."""
    syms, seen, periods = [], set(), set()
    with opener(_stock_prices_path(instance_dir)) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            t, sym, _price = line.split()
            periods.add(int(t))
            if sym not in seen:
                seen.add(sym)
                syms.append(sym)
    return syms, len(periods)


def variable_order(instance_dir, ub):
    """1-based index -> ('x', symbol, tau, period) | ('slack',).

    Matches Zimpl's creation order for the shipped model:
      var x[SX*TX] with SX = S x {1..ub} x {1,-1}, then y[CS1*TX], s2[CS2*TX].
    """
    syms, T = symbols_and_periods(instance_dir)
    order = []
    for sym in syms:
        for _m in range(1, ub + 1):
            for tau in (1, -1):
                for t in range(T):
                    order.append(("x", sym, tau, t))
    n_slack = (len(range(4)) + len(range(7))) * T  # |CS1|=4, |CS2|=7
    order.extend(("slack",) for _ in range(n_slack))
    return order


def counts_from_index(order, index_val_pairs):
    """index_val_pairs: iterable of (1-based index, value)."""
    counts = defaultdict(lambda: [0, 0])
    for idx, v in index_val_pairs:
        if v == 0:
            continue
        if idx < 1 or idx > len(order):
            raise SystemExit(f"variable index {idx} out of range 1..{len(order)}")
        entry = order[idx - 1]
        if entry[0] != "x":
            continue
        _, sym, tau, t = entry
        counts[(t, sym)][0 if tau == 1 else 1] += v
    return counts


def counts_from_uqo_index(instance_dir, sol_path, ub):
    order = variable_order(instance_dir, ub)
    objective = None
    pairs = []
    with open(sol_path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line.startswith("#"):
                m = re.search(r"Objective value\s*=\s*(-?[\d.eE+]+)", line)
                if m:
                    objective = m.group(1)
                continue
            name, val = line.split()
            mm = re.match(r"[A-Za-z_]+#(\d+)$", name)
            if not mm:
                raise SystemExit(f"not a uqo-index variable name: {name}")
            pairs.append((int(mm.group(1)), round(float(val))))
    return counts_from_index(order, pairs), objective


def counts_from_bitstring(instance_dir, sol_path, ub):
    order = variable_order(instance_dir, ub)
    objective = None
    bits = []
    with open(sol_path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line.startswith("#"):
                m = re.search(r"Objective value\s*=\s*(-?[\d.eE+]+)", line)
                if m:
                    objective = m.group(1)
                continue
            bits.append(round(float(line.split()[0])))
    if len(bits) != len(order):
        raise SystemExit(
            f"bitstring length {len(bits)} != model variable count {len(order)}; "
            "this solution is not for a shipped portfolio model")
    pairs = [(i + 1, b) for i, b in enumerate(bits)]
    return counts_from_index(order, pairs), objective


# --------------------------------------------------------------------------- #
# format detection
# --------------------------------------------------------------------------- #
def detect_format(sol_path):
    """Return 'bqp-lp', 'uqo-index' or 'bitstring'."""
    with open(sol_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            tok = line.split()[0]
            if tok.startswith("x$") or tok.startswith("y#") or tok.startswith("s2#"):
                return "bqp-lp"
            if re.match(r"[A-Za-z_]+#\d+$", tok):
                return "uqo-index"
            if re.fullmatch(r"-?\d+(\.\d+)?", tok):
                return "bitstring"
            raise SystemExit(f"cannot detect solution format from token {tok!r}")
    raise SystemExit("empty solution file")


def main():
    argv = [a for a in sys.argv[1:]]
    ub = DEFAULT_UB
    objective_override = None
    for flag in ("--ub", "--objective"):
        if flag in argv:
            i = argv.index(flag)
            val = argv[i + 1]
            del argv[i:i + 2]
            if flag == "--ub":
                ub = int(val)
            else:
                objective_override = val
    if len(argv) < 5:
        raise SystemExit(__doc__)
    model_ref, sol_path, instance, budget, lam = argv[:5]
    out = argv[5] if len(argv) > 5 else None

    fmt = detect_format(sol_path)
    if fmt == "bqp-lp":
        if os.path.isdir(model_ref):
            raise SystemExit(
                "bqp-lp solution needs the LP file as the model reference, "
                f"got directory {model_ref}")
        counts, objective = counts_from_bqp_lp(model_ref, sol_path)
    else:
        if not os.path.isdir(model_ref):
            raise SystemExit(
                f"{fmt} solution needs the instance directory as the model "
                f"reference, got {model_ref}")
        if fmt == "uqo-index":
            counts, objective = counts_from_uqo_index(model_ref, sol_path, ub)
        else:
            counts, objective = counts_from_bitstring(model_ref, sol_path, ub)

    lines = [f"# converted from {sol_path.rsplit('/', 1)[-1]} ({fmt})",
             f"instance {instance}",
             f"budget {budget}",
             f"lambda {lam}"]
    # --objective overrides whatever the solver emitted (or fills the gap when
    # the solver doesn't emit an objective comment at all).
    if objective_override is not None:
        objective = objective_override
    if objective is not None:
        # The reference objective is provably integer: every coefficient is a
        # Zimpl round(...) and all variables are binary (upscale = 1). Solvers
        # report it as a float with tiny numerical noise (e.g. -31504.0140...),
        # which the exact-arithmetic checker would reject. Round to the nearest
        # integer so the claimed value matches the recomputed one bit-for-bit.
        lines.append(f"objective {round(float(objective))}")
    lines.append("# period symbol long short")
    for (t, sym), (lo, sh) in sorted(counts.items()):
        lines.append(f"{t} {sym} {lo} {sh}")
    text = "\n".join(lines) + "\n"
    if out:
        with open(out, "w") as fh:
            fh.write(text)
        print(f"wrote {out}")
    else:
        sys.stdout.write(text)


if __name__ == "__main__":
    main()
