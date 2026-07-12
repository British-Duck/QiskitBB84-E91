from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

qc = QuantumCircuit(1, 1)   # 1 qubit, 1 classical bit for the result
qc.h(0)                     # Hadamard on qubit 0
qc.measure(0, 0)            # measure qubit 0 into classical bit 0

sim = AerSimulator()
result = sim.run(transpile(qc, sim), shots=1000).result()
print(result.get_counts())