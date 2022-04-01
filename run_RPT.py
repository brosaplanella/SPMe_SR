import pybamm
import os
import gc
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from auxiliary_functions import create_filename, run_RPT


plt.style.use(["science", "vibrant"])

mode = "presentation"

if mode == "presentation":
    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "text.usetex": False,
        }
    )
    plt.rcParams.update(
        {
            "font.size": 10,
            "axes.labelsize": 12,
            "lines.linewidth": 2,
        }
    )


elif mode == "paper":
    plt.rcParams.update(
        {
            "font.size": 8,
            "axes.labelsize": 10,
        }
    )


N_cycles = 2000
C_ch = 1 / 3
C_dch = 1

options = {"SEI": True, "plating": False, "porosity": True}

# SPMe = pybamm.load_sim(
#     os.path.join(
#         "data",
#         "sim_"
#         + create_filename({"name": "SPMe_SR", **options}, C_dch, C_ch)
#         + "_{}.pkl".format(N_cycles),
#     )
# )

# DFN = pybamm.load_sim(
#     os.path.join(
#         "data",
#         "sim_"
#         + create_filename({"name": "DFN_SR", **options}, C_dch, C_ch)
#         + "_{}.pkl".format(N_cycles),
#     )
# )

RPT_at_cycles = 10
# sims = ["SPMe_SR", "DFN_SR"]
sims = ["DFN_SR"]
C_rates = [1 / 3, 1 / 2, 1]
# C_rates = [1 / 3, 1 / 2]
# C_rates = [1]

for name in sims:
    sim = pybamm.load_sim(
        os.path.join(
            "data",
            "sim_"
            + create_filename({"name": name, **options}, C_dch, C_ch)
            + "_{}.pkl".format(N_cycles),
        )
    )
    for C_rate in C_rates:
        print("RPT for {} at {:.2f}C".format(sim.model.name, C_rate))
        # experiment = pybamm.Experiment(["Discharge at {}C until 2.5 V".format(C_rate)])
        df = run_RPT(sim, C_rate=C_rate, RPT_at_cycles=RPT_at_cycles)
        if float(C_rate).is_integer():
            C_tag = "_{:.0f}C_".format(C_rate)
        elif float(1 / C_rate).is_integer():
            C_tag = "_C{:.0f}_".format(1 / C_rate)
        else:
            C_tag = "_{:.2f}C_".format(C_rate)

        df.to_csv(
            os.path.join(
                "data",
                "RPT"
                + C_tag
                + create_filename(sim.model, C_dch, C_ch)
                + "_{}.csv".format(N_cycles),
            )
        )
        
        gc.collect()
