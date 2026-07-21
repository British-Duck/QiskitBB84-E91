"""Standalone BB84/E91 state-evolution specimens.

The trace itself lives in utils/visualise.py -- this module only supplies the
example circuits. (It previously carried its own older copy of show_evolution
that halted at measurement; the shared one traces through collapse.)
"""
import numpy as np
from qiskit import QuantumCircuit

from utils.visualise import show_evolution

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