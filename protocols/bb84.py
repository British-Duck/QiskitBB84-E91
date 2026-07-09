"""BB84 quantum key distribution - core protocol (no eavesdropper)."""
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

rng = np.random.default_rng() # initialize a random number generator (from numpy)
sim = AerSimulator() # initialize the AerSimulator for running quantum circuits

 #creates n bits with raddnom values of 0 or 1 and turn then into a numpy array
def generate_bits(n: int) -> np.ndarray:
    """Random classical bits, 0 or 1."""
    return rng.integers(0, 2, size=n) 

#creates n bases with random vlaues of 0 = z & 1 = x and turn then into a numpy array
def generate_bases(n: int) -> np.ndarray:
    """Random bases: 0 = Z basis, 1 = X basis."""
    return rng.integers(0, 2, size=n)

#encodes qubit based on the bit and basis values depending on the state Alice uses and what she prepares it with (the basis)
def encode_qubit(bit: int, basis: int) -> QuantumCircuit:
    """Alice: prepare one qubit encoding `bit` in `basis`."""
    qc = QuantumCircuit(1, 1) #initialize a quantum circuit with 1 qubit and 1 classical bit
    # if bit and basis match apply 2 or no gates to the qubit, if they don't match apply 1 gate to the qubit
    if bit == 1:
        qc.x(0)  # apply X gate to flip |0> to |1>  
    if basis == 1:
        qc.h(0)  # apply H gate to move Z states into the X basis 
    return qc #return the quantum circuit with the encoded qubit





def measure_qubit(qc: QuantumCircuit, basis: int) -> int: #uses the initialized quantum circuit and the randomly generated basis to measure the qubit and reutn a bit value
    """Bob: measure the received qubit in his chosen `basis`."""
    if basis == 1:
        qc.h(0)  # apply H gate to move X states into the Z basis
    qc.measure(0, 0) #measure qubit 0 and store the result in classical bit 0
    result = sim.run(transpile(qc, sim), shots=1).result()
    return int(list(result.get_counts().keys())[0])

def sift(a_bases, b_bases, bits) -> np.ndarray:
    """Keep only positions where Alice's and Bob's bases agree."""
    if len(a_bases) != len(b_bases) or len(a_bases) != len(bits): #checks both array lengths are the same, if not raise an error
        raise ValueError("Input arrays must have the same length.")
    matching_subset = [bits[i] for i in range(len(a_bases)) if a_bases[i] == b_bases[i]] #sift the bits based on the bases, if they match keep the bit, if not discard it
    return np.array(matching_subset)


# runs hte BB84 wiht n bits
def run_bb84(n: int = 100):
    #genrates the random bits and bases for Alice and Bob
    a_bits  = generate_bits(n)
    a_bases = generate_bases(n)
    b_bases = generate_bases(n)

    # measure the qubits based on the encoded bits and bases, and store the results in b_bits
    b_bits = np.array([
        measure_qubit(encode_qubit(a_bits[i], a_bases[i]), b_bases[i])
        for i in range(n)
    ])
     
    #sift the bits based on the bases, if they match keep the bit, if not discard it
    alice_key = sift(a_bases, b_bases, a_bits)
    bob_key   = sift(a_bases, b_bases, b_bits)
 
    #print the results of the BB84 protocol, including the number of qubits sent, the length of the sifted key, and whether Alice's and Bob's keys match
    print(f"Sent {n} qubits, sifted key length: {len(alice_key)}")
    print(f"Keys match: {np.array_equal(alice_key, bob_key)}")
    return alice_key, bob_key

# if the script is run directly, execute the run_bb84 function
if __name__ == "__main__":
    run_bb84()