"""E91 entanglement-based QKD with CHSH security test."""
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

rng = np.random.default_rng(42)
sim = AerSimulator()

# the fixed measurement angles each side randomly picks from - some overlap (for the key), some don't (for the CHSH test)
ALICE_ANGLES = [0, np.pi/4, np.pi/2]
BOB_ANGLES   = [np.pi/4, np.pi/2, 3*np.pi/4]

def make_bell_pair() -> QuantumCircuit:
    """|Phi+> = (|00> + |11>)/sqrt(2) on qubits 0 (Alice) and 1 (Bob)."""
    qc = QuantumCircuit(2, 2)
    qc.h(0) # hadamard gate puts Alice's qubit into superposition (|0>+|1>)/sqrt(2)
    qc.cx(0, 1) #cnot gate to entangle Alice's qubit with Bob's qubit
    return qc


def measure_pair(qc: QuantumCircuit, theta_a: float, theta_b: float) -> tuple[int, int]:
    """Measure qubit 0 along theta_a and qubit 1 along theta_b (x-z plane)."""
    qc.ry(-theta_a, 0) # rotate Alice's qubit (qubit 0) around the y-axis - this picks her measurement angle in the x-z plane
    qc.ry(-theta_b, 1) # rotate Bob's qubit (qubit 1) around the y-axis - this picks his measurement angle in the x-z plane
    qc.measure([0, 1], [0, 1]) # measures both qubits and stores the results in classical bits
    result = sim.run(transpile(qc, sim), shots=1).result() #run the circuit once on the simulator and get the result
    outcome = list(result.get_counts().keys())[0]      # e.g. '10' = clbit1, clbit0
    return int(outcome[1]), int(outcome[0])            # (alice_bit, bob_bit)


def measure_pair_with_eve(qc: QuantumCircuit, theta_a: float, theta_b: float,
                          theta_e: float) -> tuple[int, int]:
    """Eve intercepts Bob's qubit mid-flight: measures along theta_e, resends.

    Implemented as rotate -> mid-circuit measure -> rotate back, all on qubit 1.
    Needs a circuit with 3 classical bits (clbit 2 holds Eve's result).
    """
    # --- Eve's intercept on Bob's qubit (qubit 1) ---
    qc.ry(-theta_e, 1)      # rotate Bob's qubit around the y-axis to Eve's guessed angle (x-z plane)
    qc.measure(1, 2)        # Eve measures it mid-flight, collapsing the state
    qc.ry(theta_e, 1)       # rotates back: collapsed state now points along original axis

    # --- Alice and Bob, exactly as in the honest case ---
    qc.ry(-theta_a, 0) # creates measurement along theta_a for Alice's qubit (qubit 0)
    qc.ry(-theta_b, 1) # creates measurement along theta_b for Bob's qubit (qubit 1)
    qc.measure([0, 1], [0, 1])

    result = sim.run(transpile(qc, sim), shots=1).result()
    outcome = list(result.get_counts().keys())[0]      # e.g. '101' = clbit2,clbit1,clbit0
    return int(outcome[-1]), int(outcome[-2])          # (alice_bit, bob_bit)




def run_e91(n_pairs: int = 2000, eve_fraction: float = 0.0, verbose: bool = True, show_circuits: bool = False):
    from utils.visualise import show_evolution

    #generates the random measurement settings for Alice, Bob and Eve
    a_settings = rng.integers(0, 3, size=n_pairs)
    b_settings = rng.integers(0, 3, size=n_pairs)
    e_settings = rng.integers(0, 3, size=n_pairs)   # Eve draws from Bob's angle set

    a_bits = np.empty(n_pairs, dtype=int)
    b_bits = np.empty(n_pairs, dtype=int)
    shown_honest = shown_eve = False                # track specimens so we only print one of each
    for i in range(n_pairs):
        if rng.random() < eve_fraction:
            qc = QuantumCircuit(2, 3)               # extra clbit for Eve
            qc.h(0); qc.cx(0, 1)                    # Bell pair (inline; measure_pair_with_eve needs the 3rd clbit)
            a_bits[i], b_bits[i] = measure_pair_with_eve(
                qc, ALICE_ANGLES[a_settings[i]], BOB_ANGLES[b_settings[i]],
                BOB_ANGLES[e_settings[i]])
            if show_circuits and not shown_eve:     # specimen: trace halts at Eve's mid-circuit collapse
                show_evolution(qc.copy(), "E91 specimen - CHSH test round QC: intercepted pair")
                shown_eve = True
        else:
            qc = make_bell_pair()
            a_bits[i], b_bits[i] = measure_pair(qc, ALICE_ANGLES[a_settings[i]],
                                                    BOB_ANGLES[b_settings[i]])
            if show_circuits and not shown_honest:
                show_evolution(qc.copy(), "E91 specimen - CHSH test round QC: honest pair")
                shown_honest = True

    # --- key generation rounds ---
    # Alice and Bob keep only the bits where they measured at the SAME angle (matched settings -> perfectly correlated)
    key_mask = np.array([ALICE_ANGLES[a] == BOB_ANGLES[b] for a, b in zip(a_settings, b_settings)])
    alice_key, bob_key = a_bits[key_mask], b_bits[key_mask]

    # --- CHSH rounds ---
    # rounds where the angles differ (offsets of pi/4 or 3pi/4) become the Bell test data
    va, vb = 1 - 2*a_bits, 1 - 2*b_bits    # bits -> +/-1 eigenvalues

    # Compute the correlation function E(a_setting, b_setting) = <va * vb> for given settings
    def E(a_setting: int, b_setting: int) -> float:
        mask = (a_settings == a_setting) & (b_settings == b_setting)
        return np.mean(va[mask] * vb[mask])

    #compute the CHSH value S from the four test combinations
    S = E(0, 0) - E(0, 2) + E(2, 0) + E(2, 2)

    if verbose:
        # honest run gives near-perfect key agreement and |S| ~ 2.8; Eve drags agreement down and S back towards 2
        agree = np.mean(alice_key == bob_key) if len(alice_key) else float("nan")
        print(f"pairs={n_pairs} | key bits={len(alice_key)} | key agreement={agree:.3f} | S={S:.3f}")
    return alice_key, bob_key, S


if __name__ == "__main__":
    run_e91(eve_fraction=0.0, show_circuits=True)
    run_e91(eve_fraction=0.5)
    run_e91(eve_fraction=1.0, show_circuits=True)