# Submission for labs067

This directory contains the submission for the problem **labs067**.

| Field | Value 1 |
| --- | --- |
| Problem | labs067 |
| Submitter | CREAIM Research Team |
| Affiliation | CREAIM Inc. |
| Date | 2026-10-02 |
| Reference | https://github.com/hsm6954-boop/CREAIM-Runtime-QOBLIB-Reproducibility |
| Best Objective Value | 241 |
| Optimality Bound | N/A |
| Modeling Approach | Classical LABS search using a proprietary reduced binary encoding that deterministically maps to the full 67-spin sequence; exact LABS autocorrelation energy is used for evaluation. |
| # Decision Variables | 34 |
| # Binary Variables | 34 |
| # Integer Variables | 0 |
| # Continuous Variables | 0 |
| # Non-Zero Coefficients | N/A |
| Coefficients Type | N/A |
| Coefficients Range | N/A |
| Workflow | Load the public instance definition; execute the proprietary CREAIM Runtime classical stochastic solver under the fixed submitted run protocol; independently recompute full-sequence LABS energy; retain the best verified sequence. |
| Algorithm Type | Stochastic |
| Paradigm | Classical |
| # Runs | 5 |
| # Feasible Runs | 5 |
| # Successful Runs | 5 |
| Success Threshold | 0 |
| Hardware Specifications | Base44 sandbox; 4 vCPU x86_64 virtualized AuthenticAMD; Linux/gVisor; GCC 12.2.0; OMP_NUM_THREADS=4; no GPU; no QPU |
| Total Runtime | 19.010000 |
| Time to Solution | N/A |
| CPU Runtime | N/A |
| GPU Runtime | 0 |
| QPU Runtime | 0 |
| Other HW Runtime | 0 |
| Remarks | Reference-blind classical run. QOBLIB frozen ledger status: best known, not proven optimum. CREAIM makes no independent optimality claim. Fixed outer seeds 28123, 128126, 228129, 328132, 428135; OMP_NUM_THREADS=4. Solver build SHA-256 f1a931f89d6abb64721d4fc4edf21500cd4cbcd0f5391c46977eb6dd2a897a19. Solution SHA-256 0b005ddac03cd11ac32cc4c656b27e8bf54b3a626841d2f430325a07cd7a8086. Official QOBLIB checker source SHA-256 521a89ea4ae02e98461b053ec614d024899365631fe02c3b73b3b45e71c8beb9. |
