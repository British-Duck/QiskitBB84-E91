"""QBER vs Eve's interception fraction - the detection signature plot."""
import numpy as np
import matplotlib.pyplot as plt
from protocols.bb84 import run_bb84

fractions = np.linspace(0, 1, 11)
trials = 10          # more trials -> smaller error bars
n = 300              # more qubits -> smoother per-run QBER

mean_qbers, sem_qbers = [], []
for p in fractions:
    results = [run_bb84(n=n, eve_fraction=p, verbose=False)[2]
               for _ in range(trials)]
    mean_qbers.append(np.mean(results))
    sem_qbers.append(np.std(results) / np.sqrt(trials))  # standard error of the mean

plt.figure(figsize=(8, 5))
plt.errorbar(fractions, mean_qbers, yerr=sem_qbers, fmt="o-", capsize=4,
             label=f"simulated ({trials}-run mean, n={n})")
plt.plot(fractions, fractions / 4, "--", label="theory: QBER = p/4")
plt.axhline(0.11, color="red", ls=":", label="abort threshold ≈ 11%")

plt.xlabel("Eve's interception fraction p")
plt.ylabel("QBER")
plt.title("BB84: eavesdropping raises the quantum bit error rate")
plt.legend()
plt.grid(True, alpha=0.3)
plt.savefig("analysis/qber_vs_eve.png", dpi=150, bbox_inches="tight")
