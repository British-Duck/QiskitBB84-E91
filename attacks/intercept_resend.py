"""Eve: intercept-resend attack on the BB84 channel."""
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

from protocols.bb84 import encode_qubit

rng = np.random.default_rng()
sim = AerSimulator()

def intercept_resend(qc: QuantumCircuit, eve_basis: int) -> QuantumCircuit:
    """Eve measures the incoming qubit in her guessed basis and
    resends a fresh qubit prepared as whatever she observed."""
    if eve_basis == 1:
        qc.h(0)  # apply H gate to move X states into the Z basis
    qc.measure(0, 0) # measure qubit 0 and store the result in classical bit 0
    result = sim.run(transpile(qc, sim), shots=1).result()
    her_result = int(list(result.get_counts().keys())[0]) # Eve's measurement result    
    
    qc_resend = encode_qubit(her_result, eve_basis) # Eve prepares a new qubit based on her measurement result and basis

    return qc_resend # return the new quantum circuit with the resent qubit
