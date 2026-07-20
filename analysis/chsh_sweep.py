"""CHSH parameter S vs Eve's interception fraction - entanglement as tamper seal."""
import numpy as np
import matplotlib.pyplot as plt
from protocols.e91 import run_e91

fractions = np.linspace(0, 1, 6)
trials = 5
n_pairs = 1000        # per run; ~110 rounds behind each E term

means, sems = [], []
for p in fractions:
    s_vals = [run_e91(n_pairs=n_pairs, eve_fraction=p, verbose=False)[2]
              for _ in range(trials)]
    means.append(np.mean(s_vals))
    sems.append(np.std(s_vals) / np.sqrt(trials))

plt.figure(figsize=(8, 5))
plt.errorbar(fractions, means, yerr=sems, fmt="o-", capsize=4,
             label=f"simulated ({trials}-run mean, {n_pairs} pairs)")
plt.axhline(2*np.sqrt(2), color="green", ls="--", label="Tsirelson bound 2√2")
plt.axhline(2, color="red", ls=":", label="classical bound S = 2")
plt.xlabel("Eve's interception fraction p")
plt.ylabel("CHSH parameter S")
plt.title("E91: interception degrades the Bell violation")
plt.legend()
plt.grid(True, alpha=0.3)
plt.savefig("analysis/chsh_vs_eve.png", dpi=150, bbox_inches="tight")