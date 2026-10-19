# VQE for Maximum Independent Set (Dasgupta et al.)

Submission of 2026-08-31 for the Maximum Independent Set problem class, covering 8 instances:
C125-9, brock200-1, brock200-2, brock200-3, brock200-4, brock400-1, c-fat200-1, sloane_1dc_64.

Authors: Kalyan Dasgupta, Sumanta Mukherjee, Dhriti Verma, Surya Shravan Kumar Sajja, Abhishek Singh, Dzung Phan, Jayant Kalagnanam (IBM Research).

Reference: https://arxiv.org/abs/2606.28866

Each instance folder contains its own `README.md`, `*_summary.csv` and `*_solution.sol`.

## AI disclosure

assisted — parts of the VQE solver code were drafted with Claude Sonnet 5 (Anthropic), then reviewed and edited by the submitter. Specifically, Claude helped write the post-processing code and the circuit component that uses multi-controlled-X (MCX) gates with an ancilla to prepare a superposition of near-optimal seed bitstrings (see https://arxiv.org/abs/2606.28866). Claude also helped create the multiple solution files for this QOBLIB submission and polished the language of the submission text. The submitter, Kalyan Dasgupta, takes responsibility for the correctness of this submission and the accuracy of everything it reports.
