import os
import pybamm
import numpy as numpy
import matplotlib.pyplot as plt
from auxiliary_functions import *

pybamm.set_logging_level("INFO")

# Define models
options = {"SEI": False, "plating": True, "porosity": True}
SPMe = assemble_model({"name": "SPMe+SR", **options})
DFN = assemble_model({"name": "DFN+SR", **options})

# models = [SPMe, DFN]
models = [DFN]

# Define parameters
param = set_parameters()
param.update(
    {
        "Exchange-current density for plating [A.m-2]": 1e-3,
        "Exchange-current density for stripping [A.m-2]": 0,
    }
)

# Define experiment
N_cycles = 1
save_at_cycles = [1]
C_ch = 1 / 3
C_dch = 1

experiment = pybamm.Experiment(
    [
        ("Discharge at {}C until 2.5 V".format(C_dch),
        "Charge at {}C until 4.2 V".format(C_ch),
        "Hold at 4.2 V until C/20")
    ] * N_cycles,
    cccv_handling="ode"
)

# Solve models
sims = []
var_pts = None

for model in models:
    if model.name.startswith("DFN"):
        solver = pybamm.CasadiSolver(mode="fast with events")
    else:
        solver = pybamm.CasadiSolver(mode="fast with events")
    #     var = pybamm.standard_spatial_vars
    #     var_pts = {var.x_n: 30, var.x_s: 30, var.x_p: 200, var.r_n: 10, var.r_p: 10}

    sim = pybamm.Simulation(
        model, 
        parameter_values=param, 
        experiment=experiment, 
        solver=solver,
        var_pts=var_pts,
    )
    sim.solve(save_at_cycles=save_at_cycles)
    filename = create_filename(model, C_dch, C_ch)
    sim.save(os.path.join(
        "data",
        "sim_" + filename + "_{}.pkl".format(N_cycles),
    ))
#     sims.append(sim)

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
#         "Total SEI thickness [m]",
#         "X-averaged total SEI thickness [m]",
#         "Loss of capacity to SEI [A.h]",
#         # "Negative electrode porosity",
#         "X-averaged negative electrode porosity",
#         # "Negative electrode SEI interfacial current density",
#         "X-averaged SEI interfacial current density [A.m-2]",
#         # "Negative electrode interfacial current density",
#         "Terminal voltage [V]"
#     ]
# )
