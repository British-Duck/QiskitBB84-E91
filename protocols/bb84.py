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

def qber(alice_key, bob_key) -> float:
    """Quantum Bit Error Rate (QBER) between Alice's and Bob's sifted keys."""
    if len(alice_key) != len(bob_key): #checks both array lengths are the same, if not raise an error
        raise ValueError("Input arrays must have the same length.")
    if len(alice_key) == 0: #if the length of the array is 0 return 0.0
        return 0.0
    errors = np.sum(alice_key != bob_key) #count the number of bits that don't match between Alice and Bob
    return errors / len(alice_key) #return the number of errors divided by the total number of bits in the key

# runs BB84 with n qubits; eve_fraction = probability Eve intercepts each qubit
def run_bb84(n: int = 100, eve_fraction: float = 0.0, verbose: bool = True):
    from attacks.intercept_resend import intercept_resend  # local import avoids circular dependency

    a_bits  = generate_bits(n)
    a_bases = generate_bases(n)
    b_bases = generate_bases(n)
    e_bases = generate_bases(n)  # Eve's basis guesses (only used where she intercepts)

    b_bits = np.empty(n, dtype=int)
    for i in range(n):
        qc = encode_qubit(a_bits[i], a_bases[i])      # Alice prepares, sends into channel
        if rng.random() < eve_fraction:                # Eve intercepts this qubit with probability eve_fraction
            qc = intercept_resend(qc, e_bases[i])      # Eve measures + resends her reconstruction
        b_bits[i] = measure_qubit(qc, b_bases[i])      # Bob measures whatever arrives

    alice_key = sift(a_bases, b_bases, a_bits)
    bob_key   = sift(a_bases, b_bases, b_bits)
    error_rate = qber(alice_key, bob_key)

    if verbose:
        print(f"eve_fraction={eve_fraction:.2f} | sent {n} | sifted {len(alice_key)} | QBER {error_rate:.3f}")
    return alice_key, bob_key, error_rate
   



# if the script is run directly, execute the run_bb84 function. Runs both wiht and wihtout eve's interception to show the difference in QBER (Quantum Bit Error Rate)
if __name__ == "__main__":
    run_bb84(eve_fraction=0.0)
    run_bb84(eve_fraction=1.0)