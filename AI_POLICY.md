# AI Policy

QOBLIB accepts submissions prepared with the help of AI tools, provided
the use is disclosed and a named person is responsible for the submission.

1. **Responsibility.** 
   Every submission is made by a named person who vouches for its correctness and for the accuracy of everything it reports, regardless of how it was produced. 
   AI tools are not listed as authors or submitters, and automated agents may not open or merge pull requests. 
   Maintainers may close a submission whose open questions are not resolved, and may remove an accepted one if its reported data turn out to be inaccurate.

2. **Disclosure.** 
   Each submission declares one of:
   - `none`: no AI-generated content in the submission.
   - `assisted`: parts of the code or text were AI-generated, then reviewed and edited by the submitter.
   - `generated`: the solver code or write-up is predominantly AI-generated.
   
   For `assisted` and `generated`, name the tool and model version and say which parts it produced.
   The declaration goes in the pull request description and in the `README.md` at the submission root.

3. **AI as the method.** 
   If an AI system is part of the optimization method itself (for example an LLM proposing heuristics or solutions), describe it in the method description like any other algorithmic component, including model and version.

4. **Not covered.** 
   Using AI for literature search, debugging, or checking your own work needs no disclosure as long as its output is not part of the submission.

5. **Same bar for everyone.** 
   Disclosure neither lowers nor raises the acceptance criteria. 
   All solutions must pass the checker.
