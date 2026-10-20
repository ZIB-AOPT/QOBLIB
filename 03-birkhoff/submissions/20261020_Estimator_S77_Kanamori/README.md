# Estimator S77: fixed-instance B3_3_1 integration experiment

Submitter: Kenji Kanamori, Independent Researcher. Date: 2026-10-20.

This submission reports a fixed-instance simulator integration experiment. Five independently acquired datasets were processed by the fixed proprietary S77 estimator. All five produced a decomposition with objective value 2; all five passed local execution of a saved official QOBLIB Birkhoff checker v1.2. No run in this reported five-run experiment ended without an output. This is not QOBLIB maintainer acceptance or independent certification of the estimator or its speed.

## Scope and limitations

- This experiment reused the instance-specific phase-selector state-preparation circuit from the earlier R5 experiment. It does not establish a general solver for unseen optimization instances.
- The preparation circuit was re-executed for each new acquisition. The measurement interface was adapted for S77, including analysis-basis changes and auxiliary/reference observations. Only the problem variables contributed to the submitted solution. Internal acquisition structure and settings are withheld; no claim of complete public reproducibility is made.
- The timed S77 processing consumed the recorded measurements from those five fresh acquisitions. It did not execute a quantum simulator or QPU in the timed interval.
- Target problem measurements were shared with the R5 comparison arm. Reference and auxiliary resources differed between the two arms, so this is not an equal-resource speed comparison.
- End-to-end Total Runtime, Time to Solution and CPU Runtime were not measured across the full acquisition-to-solution workflow and are reported as N/A. Estimator throughput is a separate, explicitly bounded supplemental observation. Missing runtime information has not been inferred from it.

## External workflow

Read the public B3_3_1 instance; execute the inherited fixed-instance state preparation with the versioned acquisition interface; process the measurements through S77; map the released selection to permutations; compute exact weights using only the selected permutations; validate the resulting decomposition. There was no post-output search for alternative supports or final solution repair. This describes the outer workflow, not the confidential estimator algorithm.

The solution uses two permutation matrices. The selection model has six binary variables; exact weight reconstruction is post-processing. No proven optimality bound is asserted. Official reference solutions/checker output were not used as pre-release estimator inputs. The inherited, instance-specific nature of state preparation is explicitly disclosed above.

Setup/formatting failures occurred while commissioning the acquisition interface and were retained privately. They were not additional independent runs in this fixed five-run comparison. The five reported acquisitions were not selected by testing whether their estimator output matched a reference solution. Reprocessing a recorded acquisition is not counted as a new independent acquisition.

## Environment and identity

Estimator host: HP OmniBook 5 Laptop 16-af1xxx; Intel Core Ultra 5 225U; 12 physical cores / 14 logical processors; 16,602,746,880 bytes physical memory; Windows 11; Python 3.12.10. No GPU or QPU was used.

Acquisition environment: Linux x86_64; Python 3.12.14; Qiskit 2.5.1; Qiskit Aer 0.17.2. Complete CPU/RAM specifications of the acquisition host were not retained in the experiment record; this is a hardware-reporting limitation. No acquisition speed or complete-workflow timing claim is made.

S77 experiment build fingerprint: ba4dcc73e2965504e486c67ee60d67eb643a66e0c9d6f8fa2a3f6d1048470ab8.
The implementation remains proprietary. Raw measurements, internal settings, seeds, component timings and internal inventories are retained privately. Public evidence consists only of solutions, result counts, necessary external-method disclosures, execution environment and aggregate timing.

## Supplemental timing

One warm batch processed five pre-acquired input bundles in 1.8716621000203304 seconds, approximately 2.67 bundles/second. The interval starts at input dispatch and ends at the last durable estimator output. It excludes prior measurement acquisition/simulation, estimator startup, final teardown, diagnostic file writes, and subsequent solution reconstruction/checking. It is a self-measured short-batch observation, not sustained throughput, single-input latency, comparative speed superiority or independent verification. See speed_summary.json.

## Validation

The original five result records each passed saved official checker v1.2 locally. The final submission structure and its one distinct solution file also passed local validation with the current official submission checker and a freshly compiled current-source Birkhoff checker (exit 0; 1/1 instance). See B3_3_1/validation_summary.json. This recheck does not count as a new independent experiment. Local checks establish the submitted solution's validity under the checker contract; they do not establish every claim about internal implementation. Runtime N/A values are disclosed limitations even if the CSV parser accepts them. Additional reporting may be requested by maintainers.

## AI disclosure

generated — OpenAI ChatGPT/Codex produced implementation and documentation under Kenji Kanamori's direction. Kenji Kanamori conceived and designed the algorithm, basic design and system architecture and remains the responsible human submitter. AI tools are not authors or submitters and were not invoked as live LLM components of this benchmark pipeline.

Exact model/version identifiers for the current development sessions are unavailable in the retained experiment metadata. No model identifier is inferred from a product name or from earlier R5 sessions. This is a version-disclosure limitation that may require follow-up under QOBLIB's AI policy.

The final pull request must be opened by the human submitter, as required by QOBLIB's AI policy.

## Sources and attribution

Problem data: QOBLIB — Quantum Optimization Benchmarking Library, B3_3_1 in https://github.com/ZIB-AOPT/QOBLIB/blob/main/03-birkhoff/instances/qbench_03_sparse.json, licensed CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/). The submitted decomposition is newly produced by the disclosed experiment; the public instance matrix is retained in the solution format.

Official checker/tooling: https://github.com/ZIB-AOPT/QOBLIB/tree/main/03-birkhoff/check and https://github.com/ZIB-AOPT/QOBLIB/blob/main/misc/ci/check_submission.py. Earlier R5 submission: https://github.com/ZIB-AOPT/QOBLIB/pull/76.
