# Contributing to QOBLIB

We welcome contributions to the Quantum Optimization Benchmarking Library! This guide outlines how to submit solutions and report benchmarking results.

## Submission Process

To contribute a solution to any problem instance, please submit your results via **Pull Request** to this repository. 

Please follow the guidelines below when preparing your submission.

## Validating Your Submission

Before submitting, validate your submission structure and contents using the automated checker tool provided in [misc/check_submission.py](misc/check_submission.py). 
The checker verifies directory structure, CSV format consistency, and can optionally validate solutions. For detailed usage instructions and options, see [misc/README.md](misc/README.md).

## Submission Requirements

Each benchmark submission should include:

### Required Information

1. **Problem instance identifier** - Which instance(s) were solved
2. **Submitter details** - Name(s) and affiliation(s)
3. **Submission date**
4. **Best objective value found** (for optimization problems)
5. **Solution file** - In the format specified for the problem class (see solution folders)
6. **Reference** - Link to paper, code repository, or detailed documentation with:
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
- **CPU Runtime** - Classical processing time
- **GPU Runtime** - GPU acceleration time (if applicable)
- **QPU Runtime** - Quantum processing unit time (if applicable)
- **Other Hardware Runtime** - Any additional specialized hardware

> **Note:** For multiple runs, report the average runtime. Distributions of runtimes and correlations with solution quality are encouraged to be described in referenced publications.

## Benchmark Reporting Template

We provide a CSV template for standardized submissions: [submission_template.csv](misc/submission_template.csv)

The template includes the following fields:

| Field                        | Description                                                                                                                                                                                                                               |
| ---------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Problem**                  | Identifier of the considered problem instance                                                                                                                                                                                             |
| **Submitter**                | Name(s) of the submitter(s) and affiliation(s)                                                                                                                                                                                            |
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
| **\# Runs**                  | The number of times the experiment has been repeated                                                                                                                                                                                      |
| **\# Feasible Runs**         | The number of times a run found a feasible solution                                                                                                                                                                                       |
| **\# Successful Runs**       | Number of runs that found a feasible solution with objective value $\leq (1 + \epsilon) * f_{min}$ (minimization) or $\geq (1 - \epsilon) * f_{max}$ (maximization), where $f_{min}/f_{max}$ is the best solution found by the algorithm. |
|                              |
| **Success Threshold**        | The threshold ε to define a successful run                                                                                                                                                                                                |
|                              |                                                                                                                                                                                                                                           |
| **Hardware Specifications**  | Specifications of hardware used to run the workflow                                                                                                                                                                                       |
|                              |                                                                                                                                                                                                                                           |
| **Total Runtime**            | Total runtime to run the complete workflow                                                                                                                                                                                                |
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
- Run multiple independent trials (recommend 10+ runs)
- Report statistical measures (mean, median, std dev) when possible
- Document random seeds for reproducibility

### Runtime Measurements
- Measure wall-clock time for total runtime
- Separate classical and quantum processing times
- Exclude compilation and queue times
- Report hardware specifications completely

## Questions?

If you have questions about the submission process or guidelines, please contact the maintainers or open an issue in this repository.

**Maintainers:**
- **Maximilian Schicker** - schicker@zib.de
- **Thorsten Koch** - koch@zib.de
- **Christa Zoufal** - OUF@zurich.ibm.com
- **Stefan Wörner** - WOR@zurich.ibm.com

Thank you for contributing to QOBLIB!
