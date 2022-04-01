#
# Plot system size for different mesh sizes
#

import numpy as np
import matplotlib.pyplot as plt
import os

plt.style.use(["science", "vibrant"])

mode = "paper"
save_plots = True

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
            "mathtext.default": "regular",
            "text.usetex": False,
            "font.size": 6,
            "axes.labelsize": 8,
        }
    )

def DFN_rhs_size(Nx, Nr, k=1):
    return 2 * Nx * Nr + (3 + k) * Nx + 1

def DFN_algebraic_size(Nx):
    return 5 * Nx

def SPMe_rhs_size(Nx, Nr, k=1):
    return 2 * Nr + (3 + k) * Nx + 1

Nxs = [30, 60, 120, 240]
Nrs = [10, 20, 40, 80]

fig, axes = plt.subplots(1, 1, figsize=(2.8, 2))
Nx = np.linspace(30, 240)
for Nr in Nrs:
    axes.plot(Nx, DFN_rhs_size(Nx, Nr, 1) + DFN_algebraic_size(Nx), label="$N_r$ = {}".format(Nr))

axes.plot(Nx, DFN_algebraic_size(Nx), label="algebraic eq.", color="black", linestyle="--")

axes.set_xlabel("$N_x$")
axes.set_ylabel("System size DFN+SR")
axes.legend()

fig.savefig(
    os.path.join("figures", "system_size_DFN.png"),
    dpi=300,
)

fig.tight_layout()

fig, axes = plt.subplots(1, 1, figsize=(2.8, 2))
Nx = np.linspace(30, 240)
for Nr in Nrs:
    axes.plot(Nx, SPMe_rhs_size(Nx, Nr, 1), label="$N_r$ = {}".format(Nr))

axes.set_xlabel("$N_x$")
axes.set_ylabel("System size SPMe+SR")
axes.legend()
fig.tight_layout()

fig.savefig(
    os.path.join("figures", "system_size_SPMe.png"),
    dpi=300,
)

plt.show()