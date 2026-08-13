# This file is part of QOBLIB - Quantum Optimization Benchmarking Library
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Submission compute-paradigm classification.

Real quantum hardware vs. simulated quantum vs. classical. The QUBO/Ising
*formulation* is deliberately NOT a quantum signal — classical heuristics
(abs2, tabu, simulated annealing, ...) routinely solve QUBOs. We key off the
algorithm and the hardware instead. The frontend mirrors this logic in
``classifySubmission`` (assets/common.js); keep the two in sync.
"""

from __future__ import annotations

import re

from .text import num_or_none


_QUANTUM_RE = re.compile(
    r"\bqaoa\b|\bvqe\b|\bqite\b|\bqpe\b|variational quantum|quantum approximate optimization|"
    r"quantum anneal|adiabatic quantum|grover|amplitude (?:amplification|estimation)|"
    r"quantum circuit|state ?vector|\bqubits?\b|\bqpu\b|\bd-?wave\b",
    re.IGNORECASE,
)
_SIM_RE = re.compile(
    r"simulat|state ?vector|emulat|noiseless|\baer\b|tensor[- ]?network sim|mps sim",
    re.IGNORECASE,
)
_REAL_HW_RE = re.compile(
    r"\bqpu\b|ibm[\s_-]?(?:q|quantum|fez|eagle|heron|brisbane|sherbrooke|torino|kyiv|marrakesh|"
    r"nazca|cusco|kawasaki|aachen)|\baqt\b|ibex|ionq|quantinuum|\bh1-|\bh2-|rigetti|aspen|"
    r"d-?wave|advantage|2000q|quera|aquila|pasqal|\boqc\b|sycamore|infleqtion|\biqm\b",
    re.IGNORECASE,
)


# Explicit "Paradigm" column values (controlled vocabulary in the submission
# template) → canonical category. When a submitter declares the paradigm we trust
# it over the heuristics below; the regexes only fire when this column is absent.
_PARADIGM_MAP = {
    "classical": "classical",
    "quantum hardware": "quantum_hw",
    "quantum simulator": "quantum_sim",
}


def classify_submission(sub: dict) -> str:
    """Return 'quantum_hw', 'quantum_sim', or 'classical' for a submission row.

    Prefer the submitter-declared ``Paradigm`` column when it carries a known
    value; otherwise fall back to inferring from the algorithm/hardware text.
    """
    declared = _PARADIGM_MAP.get(str(sub.get("paradigm") or "").strip().lower())
    if declared:
        return declared

    qpu = num_or_none(sub.get("runtime_qpu"))
    hw = str(sub.get("hardware") or "")
    wf = str(sub.get("workflow") or "")
    txt = " ".join(
        str(sub.get(k) or "")
        for k in ("modeling_approach", "workflow", "hardware", "algorithm_type", "reference", "remarks")
    )

    is_quantum = (qpu is not None and qpu > 0) or bool(_QUANTUM_RE.search(txt))
    if not is_quantum:
        return "classical"
    if qpu is not None and qpu > 0:
        return "quantum_hw"
    if _SIM_RE.search(txt):
        return "quantum_sim"
    if _REAL_HW_RE.search(hw) or _REAL_HW_RE.search(wf):
        return "quantum_hw"
    return "quantum_sim"


def is_infeasible_sub(sub: dict) -> bool:
    """A submission with an explicit '# Feasible Runs' == 0 produced no valid solution."""
    nf = num_or_none(sub.get("n_feasible"))
    return nf is not None and nf == 0
