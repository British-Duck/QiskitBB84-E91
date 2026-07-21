"""Shared circuit visualisation: diagram + state evolution at each timestep.
 
State printout uses Dirac notation. NOTE Qiskit's little-endian convention:
in |b1 b0>, the RIGHTMOST bit is qubit 0. So |01> means q1=0, q0=1.
 
Measurements no longer halt the trace: an outcome is sampled (seeded RNG,
reproducible), the collapsed state is shown, and evolution continues. This
lets the Eve specimen display the full intercept-resend story.
"""
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

_SEED = 42

def _dirac(sv: Statevector, tol: float = 1e-9) -> str:
    """Format a statevector as e.g. '0.707|00> + 0.707|11>' (3 d.p.)."""
    n = sv.num_qubits
    terms = []
    for i, amp in enumerate(sv.data):
        if abs(amp) < tol:
            continue
        label = format(i, f"0{n}b")          # binary index = |q_{n-1}...q_0>
        if abs(amp.imag) < tol:
            sign = "-" if amp.real < 0 else "+"
            coeff = f"{abs(amp.real):.3f}"
        else:                                 # rare here, but be honest
            sign = "+"
            coeff = f"({amp.real:.3f}{amp.imag:+.3f}i)"
        terms.append(f"{sign} {coeff}|{label}\u27e9")
    out = " ".join(terms)
    return out[2:] if out.startswith("+ ") else out

def _annotated(qc: QuantumCircuit) -> QuantumCircuit:
    """Copy of qc with a labelled barrier after each gate: t1, t2, ..."""
    out = QuantumCircuit(qc.num_qubits, qc.num_clbits)
    t = 1
    for inst in qc.data:
        if inst.operation.name == "barrier":
            continue
        q_idx = [qc.find_bit(q).index for q in inst.qubits]
        c_idx = [qc.find_bit(c).index for c in inst.clbits]
        out.append(inst.operation, q_idx, c_idx)
        out.barrier(label=f"t{t}")
        t += 1
    return out

def show_evolution(qc: QuantumCircuit, title: str):
    """Print the circuit (timesteps labelled) and the state after every step.
 
    Measurements are sampled with a seeded RNG: the printed bit value is one
    reproducible possibility, and the trace continues with the collapsed state.
    """
    print(f"\n=== {title} ===")
    print("(kets are little-endian: |q1 q0\u27e9 -- rightmost bit is qubit 0)")
    print(_annotated(qc).draw(output="text"))
    sv = Statevector.from_label("0" * qc.num_qubits)
    sv.seed(_SEED)
    print(f"t=0 |start\u27e9 = {_dirac(sv)}")

    t = 1
    for inst in qc.data:
        name = inst.operation.name
        if name == "barrier":
            continue
        q_idx = [qc.find_bit(q).index for q in inst.qubits]

        if name == "measure":
            c_idx = [qc.find_bit(c).index for c in inst.clbits]
            outcome, sv = sv.measure(q_idx)
            sv.seed(_SEED + t)               # keep later measurements reproducible
            print(f"t={t} MEASURE q{q_idx[0]} -> bit value {outcome} "
                  f"(stored in clbit {c_idx[0]})")
            print(f"      state collapses to: {_dirac(sv)}")
        else:
            step = QuantumCircuit(qc.num_qubits)
            step.append(inst.operation, q_idx)
            sv = sv.evolve(step)
            print(f"t={t} after {name}{q_idx}: {_dirac(sv)}")
        t += 1