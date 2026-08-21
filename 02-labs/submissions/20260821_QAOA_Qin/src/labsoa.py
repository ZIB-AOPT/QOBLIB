"""QAOA solver for the QOBLIB LABS problem (algorithm only).

LABS objective, HUBO cost Hamiltonian as Pauli Z-strings, QAOA circuit,
and the variational solve routine. No submission-format knowledge here.
"""

import time
import numpy as np
from qiskit import QuantumCircuit, QuantumRegister
from qiskit_aer.primitives import SamplerV2
from scipy.optimize import minimize


def energy_bits(bits):
    """LABS energy; QOBLIB convention bit 0 -> +1, bit 1 -> -1."""
    s = [1 - 2*b for b in bits]
    n = len(s)
    return sum(sum(s[i]*s[i+k] for i in range(n-k))**2 for k in range(1, n))


def hubo_terms(n):
    """LABS HUBO (AQT closed form) as list of (qubits, coeff) Z-strings."""
    terms = []
    for i in range(1, n - 1):                       # quadratic: Z_i Z_{i+2k}
        for k in range(1, (n - i)//2 + 1):
            terms.append(((i-1, i+2*k-1), 1.0))
    for i in range(1, n - 2):                       # quartic: 2 Z_i Z_{i+t} Z_{i+k} Z_{i+k+t}
        for t in range(1, (n - i - 1)//2 + 1):
            for k in range(t + 1, n - i - t + 1):
                terms.append(((i-1, i+t-1, i+k-1, i+k+t-1), 2.0))
    return terms


def _add_zstring(qc, gamma, qubits):
    """exp(-i*gamma*Z_q0 ... Z_qm-1) via CX + RZ."""
    if len(qubits) == 1:
        qc.rz(2*gamma, qubits[0])
    else:
        target = qubits[-1]
        for q in qubits[:-1]:
            qc.cx(q, target)
        qc.rz(2*gamma, target)
        for q in qubits[:-1]:
            qc.cx(q, target)


def qaoa_circuit(n, terms, theta, p):
    """Build the p-layer QAOA circuit for LABS."""
    gamma, beta = theta
    qr = QuantumRegister(n)
    qc = QuantumCircuit(qr)
    qc.h(qr)                                        # |+>^n
    for _ in range(p):
        for qubits, coeff in terms:
            _add_zstring(qc, gamma*coeff, qubits)   # e^{-i gamma H_C}
        qc.rx(2*beta, qr)                           # e^{-i beta sum X_i}
    qc.measure_all()
    return qc


def solve(n, seed=0, p=1, shots=2048, maxiter=200):
    """One QAOA run -> (best_energy, best_bits, elapsed_seconds)."""
    terms = hubo_terms(n)
    sampler = SamplerV2(seed=seed)

    def expectation(theta):
        counts = sampler.run([qaoa_circuit(n, terms, theta, p)],
                             shots=shots).result()[0].data.meas.get_counts()
        return sum(c * energy_bits([int(o[n-1-i]) for i in range(n)])
                   for o, c in counts.items()) / shots

    t0 = time.perf_counter()
    res = minimize(expectation, [0.6, 0.4], method="COBYLA",
                   options={"maxiter": maxiter})
    counts = sampler.run([qaoa_circuit(n, terms, res.x, p)],
                         shots=8192).result()[0].data.meas.get_counts()
    out = min(counts, key=lambda o: energy_bits([int(o[n-1-i]) for i in range(n)]))
    bits = [int(out[n-1-i]) for i in range(n)]
    return energy_bits(bits), bits, time.perf_counter() - t0
