"""Show circuit diagrams with timestep barriers and the state after each gate."""
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

def show_evolution(qc: QuantumCircuit, title: str):
    """Print the circuit and the statevector after every gate (measurements skipped)."""
    print(f"\n=== {title} ===")
    print(qc.draw(output="text"))
    sv = Statevector.from_label("0" * qc.num_qubits)
    print(f"t=0  |start>      : {sv.draw('latex_source')}")
    t = 1
    for inst in qc.data:
        name = inst.operation.name
        if name in ("measure", "barrier"):
            continue                       # statevector evolution stops at collapse
        idx = [qc.find_bit(q).index for q in inst.qubits]
        step = QuantumCircuit(qc.num_qubits)
        step.append(inst.operation, idx)
        sv = sv.evolve(step)
        print(f"t={t}  after {name}{idx}: {sv.draw('latex_source')}")
        t += 1

if __name__ == "__main__":
    # BB84 example: bit=1, X basis (Alice), Bob measures in X
    bb84 = QuantumCircuit(1, 1)
    bb84.x(0); bb84.barrier(); bb84.h(0); bb84.barrier(); bb84.h(0)
    show_evolution(bb84, "BB84: encode bit=1 in X, measure in X")

    # E91 example: Bell pair, then rotations at the matched key angle pi/4
    e91 = QuantumCircuit(2, 2)
    e91.h(0); e91.cx(0, 1); e91.barrier()
    e91.ry(-np.pi/4, 0); e91.ry(-np.pi/4, 1)
    show_evolution(e91, "E91: Bell pair + matched pi/4 rotations")