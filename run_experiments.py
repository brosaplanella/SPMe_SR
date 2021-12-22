import os
import pybamm
import numpy as numpy
import matplotlib.pyplot as plt
from auxiliary_functions import *

pybamm.set_logging_level("INFO")

# Define models
options = {"SEI": True, "plating": False, "porosity": True}
SPMe = assemble_model({"name": "SPMe+SR", **options})
DFN = assemble_model({"name": "DFN+SR", **options})

models = [SPMe, DFN]

# Define parameters
param = set_parameters()

# Define experiment
N_cycles = 1000
save_at_cycles = [1]
C_ch = 1 / 2
C_dch = 2

experiment = pybamm.Experiment(
    [
        ("Discharge at {}C until 2.5 V".format(C_dch),
        "Charge at {}C until 4.2 V".format(C_ch),
        "Hold at 4.2 V until C/20")
    ] * N_cycles
)

# Solve models
solver = pybamm.CasadiSolver(mode="safe")
sims = []

for model in models:
    sim = pybamm.Simulation(
        model, 
        parameter_values=param, 
        experiment=experiment, 
        solver=solver,
    )
    sim.solve(save_at_cycles=save_at_cycles)
    filename = create_filename(model, C_dch, C_ch)
    sim.save(os.path.join(
        "data",
        "sim_" + filename + "_{}.pkl".format(N_cycles),
    ))
    # sims.append(sim)

# pybamm.dynamic_plot(
#     sims,
#     output_variables=[
#         # [
#         #     "Inner negative electrode SEI concentration [mol.m-3]",
#         #     "Outer negative electrode SEI concentration [mol.m-3]",
#         # ],
#         # [
#         #     "X-averaged inner negative electrode SEI concentration [mol.m-3]",
#         #     "X-averaged outer negative electrode SEI concentration [mol.m-3]",
#         # ],
#         "Total negative electrode SEI thickness [m]",
#         "X-averaged total negative electrode SEI thickness [m]",
#         "Loss of capacity to negative electrode SEI [A.h]",
#         # "Negative electrode porosity",
#         "X-averaged negative electrode porosity",
#         # "Negative electrode SEI interfacial current density",
#         "X-averaged negative electrode SEI interfacial current density [A.m-2]",
#         # "Negative electrode interfacial current density",
#         "Terminal voltage [V]"
#     ]
# )
