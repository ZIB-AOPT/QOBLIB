# `misc/tools/` — standalone maintenance utilities

One-off / on-demand scripts used to prepare data, convert formats, and generate
documentation. Each is executable (`./<name>.py …`) and carries a shebang. The
scripts that need third-party packages declare them inline via
[PEP 723](https://peps.python.org/pep-0723/), so the zero-setup way to run them is:

```bash
uv run misc/tools/<name>.py …      # uv resolves any declared dependencies
```

The same dependencies are also available as project extras
(`uv sync --project misc --extra qubo|metrics|tables`).

| Script | Deps | Purpose |
| --- | --- | --- |
| `convert_lp2qubo.py` | `qubo` | Convert `.lp.xz` linear programs to compressed `.qs.xz` QUBO files. |
| `simplify_qubo.py` | `qubo` | Simplify a `.qs` QUBO for a linear qubit topology (SWAP-layer bound). |
| `get_metrics.py` | `metrics` | Extract model metrics from `qs_files` `.tar.gz` archives across the repo. |
| `mdutils.py` | `tables` | Markdown-table helpers; **imported** by per-problem `*/misc/*.py` scripts (not run directly). |
| `convert_info_to_md.py` | — | Convert instance `info` files to Markdown. |
| `convert_solution_to_active.py` | — | Reduce a solution to its active (non-zero) variables. |
| `generate_problem_figures.py` | — | Render the per-problem SVG figures embedded on the website. |
| `add_licence.py` | — | Add/normalise Apache-2.0 license headers on source files. |
| `rename_sol_files.sh` | — | Batch-rename solution files to the naming convention. |

## Details

### `convert_lp2qubo.py`
Converts `.lp.xz` files to compressed `.qs.xz` QUBO files (via Qiskit for the
integer→binary reformulation; all integer variables must be bounded).

```bash
uv run misc/tools/convert_lp2qubo.py <file.lp.xz>     # one file
uv run misc/tools/convert_lp2qubo.py <directory>      # every .lp.xz below it
```

### `simplify_qubo.py`
Simplifies a `.qs` QUBO to make it more suitable for quantum hardware, according
to the maximum allowed SWAP-network layers on a linear topology.
Reference: Weidenfeller et al., *Quantum* **6**, 870 (2022).

### `get_metrics.py`
Walks the project and extracts metrics from `.tar.gz` archives named `qs_files`,
writing per-directory CSVs (already-generated metrics are skipped).

```bash
uv run misc/tools/get_metrics.py --parent_dir . --directory qs_files          # whole repo
uv run misc/tools/get_metrics.py --directory <archive.tar.gz> --output_csv metrics.csv
```

> Creates a temporary directory under `/tmp`; remove it manually if the script crashes.

### `mdutils.py`
Shared Markdown-table utilities. Imported by scripts under `<problem_class>/misc/`
(e.g. `01-marketsplit/misc/sol2mdtable.py`) — kept here as the single source of
truth. Not a CLI.

### `add_licence.py`
Ensures source files carry the Apache-2.0 header.

### `rename_sol_files.sh`
Standardises solution-file names across a directory.
