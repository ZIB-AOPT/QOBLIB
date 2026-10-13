# Kenji R5 + Universal Joint - Qiskit Aer LABS submission

Submitter: Kenji Kanamori, Independent Researcher

This package contains nine locally validated LABS instances. Each instance records five actual independent stochastic runs: one provenance-audited historical run plus four fresh runs.

Workflow: public instance encoding, Qiskit Aer role acquisition, Universal Joint aggregation, fixed Kenji R5 release, decoding, then the official validator. Reference/truth data remained sealed until after release. No classical solver or final repair generated an answer.

Published evidence is limited to problem identifiers, submitted solutions, objective values, run counts, validation outcomes, aggregate runtimes, and the fixed authority hash. Fine-grained acquisition structure, randomization, component timing, internal state, and measurement records are retained privately.

Fixed Kenji R5 authority SHA-256: 958AC865431968359C3318815C198A228350982FF8D489E6BC252B57E0E3E156

RUN_QPU=false. No IBM service or quantum hardware was used.

## AI-use disclosure

- **Declaration:** `generated`.
- **Responsible submitter:** Kenji Kanamori, Independent Researcher.
- **Tools and model versions:** OpenAI ChatGPT and Codex. Retained local QOBLIB development-session metadata confirms the Codex model identifier `gpt-5.6-sol`. Exact model/version identifiers for earlier ChatGPT conversations have not been established from the retained records; this is a limitation of the historical version record, and no complete model-version history is claimed.
- **Human contribution:** Kenji Kanamori conceived and designed the algorithm, basic design, and system architecture, and directed the development.
- **AI-generated contribution:** ChatGPT/Codex generated the majority of the code implementation under that human-defined design and supported code revisions and submission documentation. The `generated` category describes the extent of AI-generated implementation/text under QOBLIB's policy; it does not attribute the algorithmic conception or architecture to the AI tool.
- **AI as the optimization method:** The disclosed ChatGPT/Codex use concerns development and documentation. They are not invoked as live LLM components of the reported benchmark execution pipeline. The reported solutions are outputs of the implemented simulation/estimation/decoding pipeline, followed by official validation.
- **Responsibility:** I, Kenji Kanamori, am the named submitter and take responsibility for the correctness of this submission and the accuracy of its reported data. AI tools are not authors or submitters.

This declaration is recorded in the pull request description and the submission-root README.md.
