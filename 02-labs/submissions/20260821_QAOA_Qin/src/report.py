"""Submission tooling for QOBLIB 02-LABS (reporting only).

Turns solve() results into the QOBLIB submission files:
    <instance>_solution.sol        (or solutions/<instance>_solution_<i>.sol)
    <instance>_summary.csv
    README.md
"""

import csv
import os

HEADER = ("Problem,Submitter,Affiliation,Date,Reference,Best Objective Value,Optimality Bound,"
          "Modeling Approach,# Decision Variables,# Binary Variables,# Integer Variables,"
          "# Continuous Variables,# Non-Zero Coefficients,Coefficients Type,Coefficients Range,"
          "Workflow,Algorithm Type,Paradigm,# Runs,# Feasible Runs,# Successful Runs,"
          "Success Threshold,Hardware Specifications,Total Runtime,Time to Solution,CPU Runtime,"
          "GPU Runtime,QPU Runtime,Other HW Runtime,Remarks")


def rle(bits):
    """Run-length code of the spin sequence (reference .sol header)."""
    s = [1 - 2*b for b in bits]
    def enc(c):
        if c < 10: return str(c)
        if c < 36: return chr(ord('a') + c - 10)
        if c < 62: return chr(ord('A') + c - 36)
        return f"<{c}>"
    out, cnt, prev = [], 0, s[0]
    for v in s:
        if v == prev: cnt += 1
        else: out.append(enc(cnt)); cnt, prev = 1, v
    out.append(enc(cnt))
    return "".join(out)


def write_sol(path, n, bits, energy):
    with open(path, "w") as fh:
        fh.write(f"# Energy: {energy}\n")
        fh.write(f"# Consecutive entries: {rle(bits)}\n")
        for b in bits:
            fh.write(f"{b}\n")


def write_summary_csv(path, n, meta):
    inst = f"labs{n:03d}"
    cfg = meta["cfg"]
    row = [inst, cfg["submitter"], cfg["affiliation"], cfg["date"], cfg["reference"],
           meta["best_E"], "N/A", cfg["model"],
           n, n, 0, 0, meta["ncoef"], cfg["coeff_type"], cfg["coeff_range"],
           cfg["workflow"], "Stochastic", "Quantum Simulator",
           meta["runs"], meta["runs"], meta["success"], "0",
           cfg["hardware"], f"{meta['total']:.3f}", f"{meta['tts']:.3f}", f"{meta['total']:.3f}",
           "N/A", "N/A", "N/A", meta["remarks"]]
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(HEADER.split(","))
        w.writerow(row)


def write_readme(path, n, meta, results, sol_paths):
    inst = f"labs{n:03d}"
    cfg = meta["cfg"]
    lines = [f"# Submission for {inst}", "",
             f"QAOA (p={meta['p']}) for the QOBLIB LABS problem at N={n}, "
             "local Aer statevector simulator.",
             "", "| Field | Value |", "| --- | --- |",
             f"| Problem | {inst} |",
             f"| Submitter | {cfg['submitter']} |",
             f"| Affiliation | {cfg['affiliation']} |",
             f"| Date | {cfg['date']} |",
             f"| Reference | {cfg['reference']} |",
             f"| Best Objective Value | {meta['best_E']} |",
             "| Optimality Bound | N/A |",
             f"| Modeling Approach | {cfg['model']} |",
             f"| # Decision Variables | {n} |",
             f"| # Non-Zero Coefficients | {meta['ncoef']} |",
             "| Paradigm | Quantum Simulator |",
             f"| # Runs | {meta['runs']} |",
             f"| # Successful Runs | {meta['success']} |",
             f"| Total Runtime [s] | {meta['total']:.3f} |", "",
             "## Per-run results", "",
             "| Run | Seed | E(S) | Runtime [s] | Solution file |",
             "| ---: | ---: | ---: | ---: | --- |"]
    for i, (E, bits, dt, seed) in enumerate(results):
        lines.append(f"| {i+1} | {seed} | {E} | {dt:.3f} | "
                     f"`{os.path.basename(sol_paths[i])}` |")
    lines.append("")
    with open(path, "w") as fh:
        fh.write("\n".join(lines))


def package_instance(inst_dir, n, results, meta):
    """Write all submission files for one instance; returns solution paths."""
    inst = f"labs{n:03d}"
    os.makedirs(inst_dir, exist_ok=True)
    results = sorted(results, key=lambda r: r[0])   # best first
    if len(results) > 1:
        sol_dir = os.path.join(inst_dir, "solutions")
        os.makedirs(sol_dir, exist_ok=True)
        sol_paths = []
        for i, (E, bits, dt, seed) in enumerate(results):
            p = os.path.join(sol_dir, f"{inst}_solution_{i}.sol")
            write_sol(p, n, bits, E)
            sol_paths.append(p)
    else:
        E, bits, dt, seed = results[0]
        p = os.path.join(inst_dir, f"{inst}_solution.sol")
        write_sol(p, n, bits, E)
        sol_paths = [p]
    write_summary_csv(os.path.join(inst_dir, f"{inst}_summary.csv"), n, meta)
    write_readme(os.path.join(inst_dir, "README.md"), n, meta, results, sol_paths)
    return sol_paths
