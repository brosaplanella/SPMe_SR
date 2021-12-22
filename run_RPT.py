import pybamm
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from auxiliary_functions import create_filename, run_RPT


# def run_RPT(simulation, experiment=None, C_rate=None):
#     # Add argument for how many/which cycles to run

#     # if experiment is None and C_rate is None:
#     #     C_rate = 0.5

#     if experiment is None:
#         experiment = pybamm.Experiment(["Discharge at C/2 until 2.5V"])

#     capacity = []
#     termination = []
#     N = len(simulation.solution.all_first_states)

#     for i, first_state in enumerate(simulation.solution.all_first_states):
#         # print output
#         print("Running RPT {} of {}".format(i + 1, N))

#         # set initial conditions
#         model = simulation.model
#         model.set_initial_conditions_from(first_state)

#         # solve cycle
#         if experiment is not None:
#             sim = pybamm.Simulation(
#                 model,
#                 experiment=experiment,
#                 parameter_values=simulation.parameter_values,
#                 # solver=simulation.solver,
#             )
#         # if C_rate is not None:
#         #     sim = pybamm.Simulation(
#         #         model,
#         #         C_rate=C_rate,
#         #         parameter_values=simulation.parameter_values,
#         #         solver=simulation.solver,
#         #     )
#         sim.solve()
#         capacity.append(sim.solution["Discharge capacity [A.h]"].entries[-1])
#         termination.append(sim.solution.termination)

#     df = pd.DataFrame(
#         data={
#             "Cycle number": range(1, N + 1),
#             "Discharge capacity [A.h]": capacity,
#             "Termination": termination,
#         }
#     )

#     return df


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


N_cycles = 1000
C_ch = 1 / 2
C_dch = 1

options = {"SEI": False, "plating": True, "porosity": True}

SPMe = pybamm.load_sim(
    os.path.join(
        "data",
        "sim_"
        + create_filename({"name": "SPMe_SR", **options}, C_dch, C_ch)
        + "_{}.pkl".format(N_cycles),
    )
)

DFN = pybamm.load_sim(
    os.path.join(
        "data",
        "sim_"
        + create_filename({"name": "DFN_SR", **options}, C_dch, C_ch)
        + "_{}.pkl".format(N_cycles),
    )
)

sims = [SPMe, DFN]
# sims = [DFN]
C_rates = [1 / 3, 1 / 2, 1]
# C_rates = [1 / 3, 1 / 2]
# C_rates = [1]

for sim in sims:
    for C_rate in C_rates:
        print("RPT for {} at {:.2f}C".format(sim.model.name, C_rate))
        experiment = pybamm.Experiment(["Discharge at {}C until 2.5 V".format(C_rate)])
        df = run_RPT(sim, experiment=experiment)
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
