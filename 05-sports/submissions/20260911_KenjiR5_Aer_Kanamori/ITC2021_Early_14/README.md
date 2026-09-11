# ITC2021_Early_14

Five independent Qiskit Aer runs produced five hard-feasible schedules.
The official RobinX validator reported infeasibility 0 for every run. Soft
objectives were [3139, 2569, 2571, 3218, 3028]; run 2 is the submitted best at
2569. Mean pipeline runtime before validation was
69.124672 seconds.

The instance has 20 teams, 38 slots and 380 matches. Execution used 38
instance-derived shards with a shared 32-qubit circuit skeleton and numeric
bindings. Universal Joint passed measurement aggregates to the Kenji R5
estimator. No classical solver or final schedule repair was used.

The estimator implementation is proprietary and absent from this package.
Only the fixed authority SHA-256 958AC865431968359C3318815C198A228350982FF8D489E6BC252B57E0E3E156 identifies it. Reference
solutions and validator results were not available before estimator release.
