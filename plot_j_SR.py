import numpy as np
import matplotlib.pyplot as plt
import os

plt.style.use(["science", "vibrant"])

mode = "paper"

if mode == "presentation":
    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "text.usetex": False,
            "font.size": 10,
            "axes.labelsize": 12,
            "lines.linewidth": 2,
        }
    )
    # plt.rcParams["axes.prop_cycle"] += cycler("linestyle", ['-', '--', ':', '-.'])


elif mode == "paper":
    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "text.usetex": False,
            "font.size": 6,
            "axes.labelsize": 8,
            "mathtext.default": "regular",
        }
    )

F = 96485

def f_EC_Atalay(x):
    return F * 4500 * 0.8e-8 / 13.2e4 * np.exp(-(x - 0.8) / 2)

def f_DMC_Atalay(x):
    return F * 4500 * 1.8e-8 / 13.2e4 * np.exp(-(x - 0.3) / 2)

def f_Li_Atalay(x):
    return 6.05e-6 / 13.2e4 * np.exp(- x / 2)

def f_SEI_Yang(x):
    return (3 * 0.68 / 1e-5) * F * 4541 * 1e-12 / 4.11e5 * np.exp(-(x - 0.8) / 2)

def f_Li_Yang(x):
    return (3 * 0.68 / 1e-5) * 1e-3 / 4.11e5 * np.exp(- x / 2)

x = np.linspace(0, 1.5)

fig, axes = plt.subplots(1, 1, figsize=(4, 2.5))

axes.plot(x, f_EC_Atalay(x), label="EC (Atalay)")
axes.plot(x, f_DMC_Atalay(x), label="DMC (Atalay)")
axes.plot(x, f_Li_Atalay(x), label="Plating (Atalay)")
axes.plot(x, f_SEI_Yang(x), label="EC (Yang)")
axes.plot(x, f_Li_Yang(x), label="Plating (Yang)")

axes.set_xlabel("Negative electrode potential [V]")
axes.set_ylabel("Ratio $\~j_{SR}$/$j_{n}$")
axes.legend()

fig.tight_layout()

fig.savefig(os.path.join("figures", "compare_j_SR.png"), dpi=300)

plt.show()
