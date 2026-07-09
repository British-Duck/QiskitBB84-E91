"""QBER vs Eve's interception fraction - the detection signature plot."""
import numpy as np
import matplotlib.pyplot as plt
from protocols.bb84 import run_bb84

fractions = np.linspace(0, 1, 11)   # p = 0.0, 0.1, ..., 1.0
trials = 5                          # average out the ~50-bit binomial noise

mean_qbers = []
for p in fractions:
    results = [run_bb84(n=200, eve_fraction=p, verbose=False)[2] for _ in range(trials)]
    mean_qbers.append(np.mean(results))

plt.plot(fractions, mean_qbers, "o-", label="simulated (5-run mean, n=200)")
plt.plot(fractions, fractions / 4, "--", label="theory: QBER = p/4")
plt.xlabel("Eve's interception fraction p")
plt.ylabel("QBER")
plt.title("BB84: eavesdropping raises the quantum bit error rate")
plt.legend()
plt.grid(True, alpha=0.3)
plt.savefig("analysis/qber_vs_eve.png", dpi=150, bbox_inches="tight")
plt.show()