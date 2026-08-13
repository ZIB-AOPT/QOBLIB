# Contributing to QOBLIB

We welcome contributions to the Quantum Optimization Benchmarking Library! This guide outlines how to submit solutions and report benchmarking results.

## Submission Process

To contribute a solution to any problem instance, please submit your results via **Pull Request** to this repository. 

Please follow the guidelines below when preparing your submission.

## Validating Your Submission

Before submitting, validate your submission structure and contents using the automated checker tool provided in [misc/ci/check_submission.py](misc/ci/check_submission.py). 
The checker verifies directory structure, CSV format consistency, and can optionally validate solutions. For detailed usage instructions and options, see [misc/README.md](misc/README.md).

The same checker runs automatically on every pull request and posts its result as a comment; a red run blocks the merge until it is fixed.

### What is required of a solution

The per-problem checkers report a fact about your solution file, and the pipeline
then applies a policy based on **what your CSV declares** (see
[misc/ci/CHECKER_CONTRACT.md](misc/ci/CHECKER_CONTRACT.md) for the full exit-code table):

- **Your solution file must always be valid** — it must parse and match the
  instance's dimensions/format. A malformed file always fails, regardless of what
  you declare.
- **Feasibility is only required if you claim it.** If a run did not produce a
  feasible solution, set **`# Feasible Runs` to `0`** for that instance. The checker
  will then accept the (valid) solution file even though it violates constraints —
  useful for reporting exploratory or withdrawn runs honestly. If `# Feasible Runs`
  is `> 0` (or left blank), at least one submitted solution file must be feasible.
- **Optimality is never required for a submission.** A valid, feasible heuristic
  solution that is not optimal is accepted. Optimality is only cross-checked when you
  **assert a proven optimum** by setting **`Optimality Bound` equal to your
  `Best Objective Value`**; leave `Optimality Bound` as `N/A` for a heuristic run.
  (`# Successful Runs` is measured against your algorithm's own best, not the global
  optimum, so it does not trigger an optimality check.) The curated best-known
  solutions under `NN-problem/solutions/` are governed separately.

### Best-known values are updated automatically

You do **not** need to touch any `solutions/` directory. When your submission is
merged, `.github/workflows/update-bkv.yml` recomputes each problem's best-known
value from the reference solutions plus every feasible submission, and:

- copies your solution file into `NN-problem/solutions/` (one file per instance)
  when it improves the best-known value, and
- regenerates the best-known table inside `NN-problem/solutions/README.md`, listing each
  instance's best-known value and the **first source** that reached it — a link to the
  crediting submission, or `reference` for a curated/literature solution.

The best-known value is awarded to the *first* source to reach it: reference
solutions are the baseline, so a submission is credited only when it is the earliest
source to strictly improve the previous best. Attribution is computed from your CSV's
`Best Objective Value` and `# Feasible Runs`, so keep those accurate. You can preview
the result locally with `uv run --project misc qoblib-update-bkv --check`.

## Submission Requirements

Each benchmark submission should include:

### Required Information

1. **Problem instance identifier** - Which instance(s) were solved
2. **Submitter details** - Name(s) of the author(s). For multiple authors, provide a comma-separated list wrapped in double quotes (e.g. `"Jane Doe, John Roe"`) so the CSV parses correctly.
3. **Affiliation** - Affiliation of the author(s). For multiple authors, provide a comma-separated list wrapped in double quotes, in the same order as the authors (e.g. `"University A, Company B"`). Repeat an affiliation when several authors share it so that the number of affiliations matches the number of authors.
4. **Submission date**
5. **Best objective value found** (for optimization problems)
6. **Solution file** - In the format specified for the problem class (see solution folders)
7. **Reference** - Link to paper, code repository, or detailed documentation with:
   - Hyperparameters
   - Complete hardware specifications
   - Software versions
   - Additional implementation details

### Model Information

- **Modeling approach** - How the problem instance was formulated
- **Decision variables** - Total count and breakdown by type:
  - Number of binary variables
  - Number of integer variables
  - Number of continuous variables
- **Coefficients**:
  - Number of non-zero coefficients (in objective and constraints)
  - Coefficient types (integer, binary, continuous)
  - Coefficient range (min/max values)

### Algorithm Details

#### Workflow Description
Briefly summarize the complete optimization workflow to facilitate reproducibility:
- **Pre-processing** - Data preparation and problem reformulation
- **Pre-solvers** - Any classical pre-solving techniques applied
- **Main optimization algorithm** - Core method used
- **Post-processing** - Solution refinement and validation

#### Algorithm Characteristics
- **Algorithm type** - Deterministic or stochastic
- **Paradigm** - Either: Classical, Quantum Simulator, Quantum Hardware
- **Optimality bound** (if available) - Lower bound (minimization) or upper bound (maximization)

#### For Stochastic Algorithms
Multiple runs are recommended. Please report:
- **\# Runs** - Total number of independent runs
- **\# Feasible Runs** - Runs that produced feasible solutions
- **\# Successful Runs** - Runs achieving near-optimal solutions within threshold
- **Success Threshold (ε)** - Number of runs that found a feasible solution with objective value $\leq (1 + \epsilon) * f_{min}$ (minimization) or $\geq (1 - \epsilon) * f_{max}$ (maximization), where $f_{min}/f_{max}$ is the best solution found by the algorithm.


### Hardware and Runtime

#### Hardware Specifications
Provide complete specifications for all hardware used in the workflow.

#### Runtime Reporting
Report average runtimes across all repetitions (exclude queuing time for hardware access):
- **Total Runtime** - End-to-end execution time
- **Time to Solution** - Time to find the best solution
- **CPU Runtime** - Classical processing time
- **GPU Runtime** - GPU acceleration time (if applicable)
- **QPU Runtime** - Quantum processing unit time (if applicable)
- **Other Hardware Runtime** - Any additional specialized hardware

> **Note:** For multiple runs, report the average runtime. Distributions of runtimes and correlations with solution quality are encouraged to be described in referenced publications.

### Objective Time Series (Optional)

To enable convergence analysis and Time-to-Solution (TTS) verification, you may include an **objective time series** file alongside your solution files.

#### File naming

Place the file in each instance subdirectory, named `<instance>_objective_time_series.json` (plain JSON) or `<instance>_objective_time_series.json.gz` (gzip-compressed for large files).

#### Format

The file must be a JSON array of *runs* (one element per independent run of your algorithm). Each run is itself an array of *incumbent update* objects recorded **whenever the best-found objective value improves**:

```json
[
  [
    {"Time": 0.001,  "Incumbent": 120.0},
    {"Time": 0.218,  "Incumbent": 5.0},
    {"Time": 0.435,  "Incumbent": 0.0}
  ],
  [
    {"Time": 0.002,  "Incumbent": 80.0},
    {"Time": 0.651,  "Incumbent": 0.0}
  ]
]
```

| Key | Type | Description |
| --- | --- | --- |
| `Time` | number | Wall-clock time in **seconds** from the start of the run at which this incumbent was first reached |
| `Incumbent` | number | The best objective value found up to this point in the run |

Rules:
- The `Incumbent` sequence within each run must be **non-increasing** for minimization problems (non-decreasing for maximization).
- The first entry should record the initial incumbent (the starting solution's objective value).
- The last entry's `Time` value should correspond to the end of the run (or the moment the algorithm terminated), so that TTS can be computed as the `Time` of the first entry whose `Incumbent` equals the final best.
- There is no required correspondence between the number of runs in the time series and `# Runs` in the CSV, but they should ideally match.

#### What the CI checker does

The automated checker validates the JSON structure (correct types, required keys, non-empty runs) and **does enforce monotonicity** — a minimization run where the incumbent increases (or a maximization run where it decreases) is reported as a hard failure that blocks the merge. Providing a time series is entirely optional; the CI checker reports its absence as informational only.

## Benchmark Reporting Template

We provide a CSV template for standardized submissions: [submission_template.csv](misc/submission_template.csv)

The template includes the following fields:

| Field                        | Description                                                                                                                                                                                                                               |
| ---------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Problem**                  | Identifier of the considered problem instance                                                                                                                                                                                             |
| **Submitter**                | Name(s) of the author(s). For multiple authors, a comma-separated list wrapped in double quotes, e.g. `"Jane Doe, John Roe"` (so the CSV parses correctly)                                                                                |
| **Affiliation**              | Affiliation of the author(s). For multiple authors, a comma-separated list wrapped in double quotes, in the same order as the authors, e.g. `"University A, Company B"`. Repeat a shared affiliation so the count matches the authors      |
| **Date**                     | Date of submission                                                                                                                                                                                                                        |
|                              |                                                                                                                                                                                                                                           |
| **Reference**                | Reference to a paper/repository with more details (number CPUs, processor types, software versions, etc.)                                                                                                                                 |
|                              |                                                                                                                                                                                                                                           |
| **Best Objective Value**     | The best objective value found by the algorithm across all repetitions                                                                                                                                                                    |
| **Optimality Bound**         | Lower bound (minimization) or upper bound (maximization) for the optimal objective value, if supported, otherwise set to N/A                                                                                                              |
|                              |                                                                                                                                                                                                                                           |
| **Modeling Approach**        | Describe how the considered problem instance is modeled                                                                                                                                                                                   |
| **\# Decision Variables**    | Total number of decision variables                                                                                                                                                                                                        |
| **\# Binary Variables**      | Number of binary decision variables                                                                                                                                                                                                       |
| **\# Integer Variables**     | Number of integer decision variables                                                                                                                                                                                                      |
| **\# Continuous Variables**  | Number of continuous decision variables                                                                                                                                                                                                   |
| **\# Non-Zero Coefficients** | Number of non-zero coefficients in objective function and constraints                                                                                                                                                                     |
| **Coefficients Type**        | Type of coefficients such as integer, binary, continuous                                                                                                                                                                                  |
| **Coefficients Range**       | Range of non-zero coefficients, i.e., min/max values                                                                                                                                                                                      |
|                              |                                                                                                                                                                                                                                           |
| **Workflow**                 | Description of the optimization workflow: pre-processing, pre-solvers, optimization algorithms, and post-processing, etc.                                                                                                                 |
| **Algorithm Type**           | Indicate whether the algorithm is deterministic or stochastic                                                                                                                                                                             |
| **Paradigm**                 | Either: Classical, Quantum Simulator, Quantum Hardware                                                                                                                                                                                    |
| **\# Runs**                  | The number of times the experiment has been repeated                                                                                                                                                                                      |
| **\# Feasible Runs**         | The number of times a run found a feasible solution                                                                                                                                                                                       |
| **\# Successful Runs**       | Number of runs that found a feasible solution with objective value $\leq (1 + \epsilon) * f_{min}$ (minimization) or $\geq (1 - \epsilon) * f_{max}$ (maximization), where $f_{min}/f_{max}$ is the best solution found by the algorithm. |
|                              |
| **Success Threshold**        | The threshold ε to define a successful run                                                                                                                                                                                                |
|                              |                                                                                                                                                                                                                                           |
| **Hardware Specifications**  | Specifications of hardware used to run the workflow                                                                                                                                                                                       |
|                              |                                                                                                                                                                                                                                           |
| **Total Runtime**            | Total runtime to run the complete workflow                                                                                                                                                                                                |
| **Time to Solution**         | Time to find the best solution                                                                                                                                                                                                            |
| **CPU Runtime**              | CPU runtime to run the workflow                                                                                                                                                                                                           |
| **GPU Runtime**              | GPU runtime to run the workflow                                                                                                                                                                                                           |
| **QPU Runtime**              | QPU runtime to run the workflow                                                                                                                                                                                                           |
| **Other HW Runtime**         | Runtime on other hardware to run the workflow                                                                                                                                                                                             |
|                              |                                                                                                                                                                                                                                           |
| **Remarks**                  | Additional notes or information                                                                                                                                                                                                           |

> **Note:** All runtimes should be reported as average if multiple algorithm runs were executed.

## Best Practices

### Solution Files
- Follow the format specified in each problem class directory
- Include validation information when applicable
- Name files according to the instance naming convention

### Documentation
- Be as detailed as possible in your reference material
- Include reproducible instructions
- Document any deviations from standard approaches
- Report negative results (valuable for the community!)

### Stochastic Algorithms
- Run multiple independent trials (recommend 10+ runs, required 5+ runs)
- Report statistical measures (mean, median, std dev) when possible
- Document random seeds for reproducibility

### Runtime Measurements
- Measure wall-clock time for total runtime
- Separate classical and quantum processing times
- Exclude compilation and queue times
- Report hardware specifications completely

## Contributing a New Problem Instance

The instance sets for each problem class are curated by the committee, but we welcome proposals to extend them — for example, when you have identified a challenging real-world graph, a larger network topology, or an instance that exercises a structural property not well covered by the existing set.

### When to propose a new instance

A new instance is appropriate when it:
- **fills a gap** in the difficulty or size range of an existing problem class (e.g. a larger size tier, a denser family, a structurally distinct graph), or
- **originates from a real application** and the committee can verify it is genuinely hard, or
- was discussed with a committee member in advance and tentatively approved.

Do **not** submit instances that are trivially solved by standard classical solvers, duplicates of existing instances, or instances without a clear source or generation procedure.

### What to include in the PR

Open a Pull Request that adds, for the relevant problem class `NN-problem/`:

1. **The instance file** placed in `NN-problem/instances/` and named according to the existing naming convention for that problem (see the `instances/README.md` of the target problem class).
2. **A reference solution** (even a heuristic or partial one) placed in `NN-problem/solutions/`. Providing at least one known feasible solution helps the committee assess difficulty.
3. **Generation provenance** — either a brief note in the PR description or a code snippet / seed value sufficient to reproduce the instance. If the instance comes from an external source, include a citation or URL.
4. **An update to `instances/README.md`** of the target problem (or a new entry in its Instance Sources list) documenting the file format, size, and origin.

### Checklist for instance PRs

Before opening the PR, verify:

- [ ] The instance file is valid and parses correctly with the problem's checker (`check/` directory).
- [ ] The naming convention matches existing instances in that problem class.
- [ ] The `instances/README.md` (or sources list) is updated.
- [ ] A reference solution or known bound is provided, even if heuristic.
- [ ] The generation procedure or external source is documented.

### Review and acceptance

Instance PRs are reviewed by at least **two committee members** who will assess difficulty, structural coverage, and provenance. Accepted instances are merged into `main` and automatically picked up by the site builder at the next deployment. Rejected instances receive a written explanation and, where possible, guidance on how to revise the proposal.

### Extending to a new problem class

If you believe an entirely new problem class should be added to QOBLIB, please **open a GitHub Issue first** to discuss scope, difficulty requirements, and the checker implementation needed before investing in a full PR. New problem classes require a problem description, model files, a solution checker, and at least a small set of reference instances, so early alignment with the committee saves significant effort.

## Questions?

If you have questions about the submission process or guidelines, please contact the maintainers or open an issue in this repository.

**Maintainers:**
- **Maximilian Schicker** - schicker@zib.de
- **Thorsten Koch** - koch@zib.de
- **Christa Zoufal** - OUF@zurich.ibm.com
- **Stefan Wörner** - WOR@zurich.ibm.com

Thank you for contributing to QOBLIB!
