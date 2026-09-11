# Kenji R5 + Universal Joint — Qiskit Aer submission

Submitter: Kenji Kanamori, Independent Researcher

This package reports seven Market Split instances, each with five independent
Qiskit Aer runs. The estimator named Kenji R5 is distinct from the submitter.
Its implementation remains proprietary and is not included. Its fixed authority
SHA-256 is 958AC865431968359C3318815C198A228350982FF8D489E6BC252B57E0E3E156.

Workflow: instance-derived encoding and numeric binding, Qiskit Aer measurement,
Universal Joint aggregation, Kenji R5 estimation, decoding, then official
validation. Reference solutions and validator results were unavailable to the
estimator before it released each output. No classical solver or final repair
generated an answer.

Simulator: Qiskit Aer 0.17.2 stabilizer. Search sampling was adaptive
(512, 512, 1024, 2048, 4096, 8192 additional shots; 16,384 maximum cumulative
shots per PUB). Universal Joint used 4,096 shots. All 35 runs were feasible and
passed the official checker.
