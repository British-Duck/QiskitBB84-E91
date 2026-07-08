from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

sim = AerSimulator() #creates an instance of the AerSimulator class, for quantum circuits and stores in sim.

# Circuit A: prepare |+>, measure in Z basis
qc_a = QuantumCircuit(1, 1) #prepares a quantum circuit with one classical bit and one qubit, stores in qc_a
qc_a.h(0) #applies a Hadamard gate to qubit 0, putting it in the |+> state  
qc_a.measure(0, 0) #measures qubit 0 and stores the result in classical bit 0

# Circuit B: prepare |0>, measure in X basis
qc_b = QuantumCircuit(1, 1) #prepares a second qc wiht 1 classical bit and 1 qubit
qc_b.h(0)
qc_b.h(0) #applies a hadamard gate to qubit 0 twice putting it back in the |0> state
qc_b.measure(0, 0)

for name, qc in [("A: X-state, Z-measure", qc_a), ("B: X-state, X-measure", qc_b)]:
    counts = sim.run(transpile(qc, sim), shots=1000).result().get_counts()
    print(name, "->", counts)