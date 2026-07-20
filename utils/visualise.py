"""Shared circuit visualisation: diagram + state evolution at each timestep."""
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

def show_evolution(qc: QuantumCircuit, title: str):
    """Print the circuit and the statevector after every gate.

    Mid-circuit measurements halt the trace (collapse is not unitary evolution).
    """
    print(f"\n=== {title} ===")
    print(qc.draw(output="text"))
    sv = Statevector.from_label("0" * qc.num_qubits)
    print(f"t=0 |start>: {sv.draw('text')}")
    t = 1
    for inst in qc.data:
        name = inst.operation.name
        if name == "barrier":
            continue
        if name == "measure":
            print(f"t={t} measure: [state collapses - trace ends]")
            break
        idx = [qc.find_bit(q).index for q in inst.qubits]
        step = QuantumCircuit(qc.num_qubits)
        step.append(inst.operation, idx)
        sv = sv.evolve(step)
        print(f"t={t} after {name}{idx}: {sv.draw('text')}")
        t += 1