#
# Get computational time DFN+SR and SPMe+SR
#

import pybamm
import numpy as np
from prettytable import PrettyTable
from auxiliary_functions import *

pybamm.set_logging_level("WARNING")

# Define models
options = {"SEI": True, "plating": False, "porosity": True}
SPMe = assemble_model({"name": "SPMe+SR", **options})
DFN = assemble_model({"name": "DFN+SR", **options})

models = [SPMe, DFN]

# Define parameters
param = set_parameters()

# Change simulation parameters here
N_solve = 2  # number of times to run the solver to get computational time
N_cycles = 10
C_chs = [1 / 3, 1 / 2]  # in degC
C_dchs = [1, 2]

tables = [PrettyTable([model.name, "1C", "2C"]) for model in models]

for i, model in enumerate(models):
    print("Running simulations for", model.name)
    for C_ch in C_chs:
        times = [None] * len(C_dchs)
        for k, C_dch in enumerate(C_dchs):
            print("Running simulation for {}C charge and {}C discharge".format(C_ch, C_dch))

            experiment = pybamm.Experiment(
                [
                    ("Discharge at {}C until 2.5 V".format(C_dch),
                    "Charge at {}C until 4.2 V".format(C_ch),
                    "Hold at 4.2 V until C/20")
                ] * N_cycles
            )
            sim = pybamm.Simulation(
                model,
                parameter_values=param,
                experiment=experiment,
            )
            time_sublist = []
            for j in range(N_solve):
                sim.solve(calc_esoh=False)
                time_sublist.append(sim.solution.solve_time)

            times[k] = time_sublist

        tables[i].add_row(
            ["{}C".format(C_ch)]
            + ["{:.2f} +- {:.2f}".format(np.mean(time), np.std(time)) for time in times]
        )

print()
print("Computational times in seconds:")
for table in tables:
    print()
    print(table)
