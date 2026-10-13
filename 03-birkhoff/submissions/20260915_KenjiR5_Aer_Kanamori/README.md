# Kenji R5 + Universal Joint - Qiskit Aer Birkhoff submission

Submitter: Kenji Kanamori, Independent Researcher

This package contains 21 Birkhoff instances. Every current instance table records five actual independent stochastic runs: one provenance-audited historical run plus four fresh runs. Acquisition components within a run are not counted as separate independent runs.

Twenty instances report five feasible and five successful runs. `B3_9_4` reports four feasible and four successful runs out of five. This package therefore does not claim that every independent run succeeded. The submitted solution and the run-count statistics are separate parts of the evidence.

The older `README_PR71.md` and `README_PR72.md` describe the two constituent subsets. Their former one-run statements have been updated to reflect the current instance tables.

## Method overview

Kenji R5 is a fixed proprietary estimator that operates on quantum measurement bundles. The benchmark pipeline starts from a public problem instance, constructs its encoding and quantum-simulator acquisition, passes the resulting measurements through the submitted estimation pipeline, decodes the released output, and then applies the official problem validator.

The estimator's role is to evaluate the measurement evidence and determine whether an output can be released; insufficient evidence is held rather than treated as a validated benchmark answer. Reference solutions and official validation results are kept outside the estimator's pre-release input. Classical processing handles the surrounding encoding, decoding, and verification; no classical solver or final repair is used to generate the submitted answer, as reported in the submission.

The implementation remains proprietary. The public interface, workflow, solution files, instance-level result tables, validation outcomes, aggregate runtimes, and fixed authority hash describe the submitted evidence. Passing the checker validates the submitted solution under its contract; it does not by itself prove every internal implementation detail.

Fixed Kenji R5 authority SHA-256: `958AC865431968359C3318815C198A228350982FF8D489E6BC252B57E0E3E156`.

`RUN_QPU=false`. These reported benchmark runs used Qiskit Aer, not IBM quantum hardware.

## AI-use disclosure

- **Declaration:** `generated`.
- **Responsible submitter:** Kenji Kanamori, Independent Researcher.
- **Tools and model versions:** OpenAI ChatGPT and Codex. Retained local QOBLIB development-session metadata confirms the Codex model identifier `gpt-5.6-sol`. Exact model/version identifiers for earlier ChatGPT conversations have not been established from the retained records; this is a limitation of the historical version record, and no complete model-version history is claimed.
- **Human contribution:** Kenji Kanamori conceived and designed the algorithm, basic design, and system architecture, and directed the development.
- **AI-generated contribution:** ChatGPT/Codex generated the majority of the code implementation under that human-defined design and supported code revisions and submission documentation. The `generated` category describes the extent of AI-generated implementation/text under QOBLIB's policy; it does not attribute the algorithmic conception or architecture to the AI tool.
- **AI as the optimization method:** The disclosed ChatGPT/Codex use concerns development and documentation. They are not invoked as live LLM components of the reported benchmark execution pipeline. The reported solutions are outputs of the implemented simulation/estimation/decoding pipeline, followed by official validation.
- **Responsibility:** I, Kenji Kanamori, am the named submitter and take responsibility for the correctness of this submission and the accuracy of its reported data. AI tools are not authors or submitters.

This declaration is recorded in the pull request description and the submission-root README.md.
