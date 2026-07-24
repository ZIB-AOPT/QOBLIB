# QOBLIB solution-checker exit-code contract

Every per-problem solution checker under `NN-problem/check/` is a small, independent
program that **reports facts about a solution file**. It does *not* decide whether a
submission is acceptable — that decision (the *policy*) lives in
[`misc/ci/check_submission.py`](check_submission.py), which combines the checker's fact
with what the submission *declares* about itself in its `*_summary.csv`.

To make that split work, every checker speaks the same exit-code language.

## Exit codes

| Code | Name | Meaning |
|------|------|---------|
| `0`  | `VALID` | The solution file is valid **and** meets the strongest target: it is feasible and, where the optimum is known (currently only LABS), optimal. |
| `20` | `SUBOPTIMAL` | The solution file is valid and **feasible**, but **not optimal**. Only checkers that know the optimum emit this (today: `02-labs`). |
| `21` | `INFEASIBLE` | The solution file parses and has the right shape, but the solution **violates a constraint** (it is infeasible / does not meet the success target). |
| `10` | `INVALID_FILE` | The solution **file itself is invalid**: unparseable, wrong length, out-of-range index, malformed format, or dimension mismatch with the instance. |
| `2`  | `USAGE` | Wrong command-line arguments, or an instance/support file could not be read. This is an *infrastructure* error, not a statement about the solution. |

Codes `20` and `21` are the only "the file is fine, the *quality* is below target"
signals, and they are the only codes the policy layer is allowed to *conditionally
accept*. Every other non-zero code (`10`, `2`, or anything unexpected such as a raw
`101` panic) is an unconditional failure.

Rule of thumb for checker authors:

* A problem with a solution-file parse error → `10` (never `20`/`21`).
* A well-formed solution that is merely infeasible → `21`.
* A well-formed, feasible solution that misses a known optimum → `20`.
* Bad CLI args or an unreadable instance file → `2`.

Parse errors are funnelled to `10` by installing a panic hook at the top of `main()`:

```rust
std::panic::set_hook(Box::new(|info| {
    eprintln!("INVALID_FILE: {info}");
    std::process::exit(10);
}));
```

so the many `panic!("Parsing solution ...")` sites in the parsers do not each need to
be rewritten.

## How the policy layer interprets these codes

`check_submission.py` reads two claims from each instance's `*_summary.csv`:

* `feas_claimed` — the submission claims it found a feasible solution.
  Derived from the `# Feasible Runs` column (blank / `N/A` ⇒ assumed feasible,
  otherwise `> 0`), matching `misc/ci/check_bkv_updates.py::_is_feasible_row`.
* `opt_claimed` — the submission asserts a *proven* optimum, expressed by the
  `Optimality Bound` meeting the `Best Objective Value`.
  `# Successful Runs` is **not** used: per `CONTRIBUTING.md` it counts runs within the
  success threshold of the *algorithm's own best*, not the global optimum, so a good
  heuristic legitimately has `# Successful Runs > 0` while remaining sub-optimal.

It then maps the checker's exit code to a verdict:

| Checker exit code | `feas_claimed` / `opt_claimed` | Verdict |
|-------------------|--------------------------------|---------|
| `10` invalid file | — | **FAIL** — a solution file must always be well-formed. |
| `2` usage/infra   | — | **FAIL** — checker could not run properly. |
| `21` infeasible   | `feas_claimed = true`  | **FAIL** — submission claims feasibility but the file is infeasible. |
| `21` infeasible   | `feas_claimed = false` | **PASS + warning** — valid file, infeasible *as declared* (e.g. a withdrawn / exploratory run). |
| `20` not optimal  | `opt_claimed = true`   | **FAIL** — submission asserts a proven optimum but the file is not optimal. |
| `20` not optimal  | `opt_claimed = false`  | **PASS + info** — valid, feasible heuristic solution; optimality was never claimed. |
| `0` valid         | — | **PASS.** (If `feas_claimed = false` yet the file is feasible, a note is emitted that the metadata under-claims.) |

Consequences:

* **Validity of the solution file is always enforced.** A malformed file fails no
  matter what the submission declares.
* **Feasibility is enforced only when claimed.** A submission that honestly declares
  `# Feasible Runs = 0` is accepted as long as its solution file is well-formed.
* **Optimality is never required for a `submissions/` entry.** It is only enforced
  when the submission itself asserts a proven optimum (`Optimality Bound` ==
  `Best Objective Value`). A heuristic that leaves `Optimality Bound` as `N/A` is
  accepted regardless of how close it is to the optimum. (Optimality of the *curated*
  best-known solutions under `NN-problem/solutions/` is governed separately by
  `misc/ci/check_bkv_updates.py`.)

### Multiple solution files

When an instance ships a `solutions/` directory with several numbered files, the rule
is applied per file with an instance-level aggregate:

* **Every** file must be valid (no file may return `10`).
* If `feas_claimed`, **at least one** file must be feasible (`0` or `20`).
* Optimality is only ever required if `opt_claimed`, and then at least one file must be
  optimal (`0`).
