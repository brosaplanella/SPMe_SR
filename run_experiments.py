import os
import pybamm
from auxiliary_functions import set_parameters, create_filename

pybamm.set_logging_level("NOTICE")

# Define models
options = {
    "SEI": "ec reaction limited",
    # "SEI": "none",
    "SEI porosity change": "true",
    "lithium plating": "irreversible",
    # "lithium plating": "none",
    "lithium plating porosity change": "true",
}
SPMe = pybamm.lithium_ion.SPMe(name="SPMe+SR", options=options)
DFN = pybamm.lithium_ion.DFN(name="DFN+SR", options=options)

models = [SPMe, DFN]

# Define parameters
param = set_parameters()

# Define experiment
N_cycles = 1000
save_at_cycles = [1]  # [1] by default to save memory
C_ch = 1 / 2
C_dch = 1

experiment = pybamm.Experiment(
    [
        (
            "Discharge at {}C until 2.5 V".format(C_dch),
            "Charge at {}C until 4.2 V".format(C_ch),
            "Hold at 4.2 V until C/20",
        )
    ]
    * N_cycles,
)

# Solve models
sims = []

for model in models:
    solver = pybamm.CasadiSolver("safe")
    sim = pybamm.Simulation(
        model,
        parameter_values=param,
        experiment=experiment,
        solver=solver,
    )
    sim.solve(save_at_cycles=save_at_cycles)
    filename = create_filename(model, C_dch, C_ch)
    # Hack to allow pickling
    # sim.op_conds_to_built_solvers = None
    sim.save(
        os.path.join(
            "data",
            "sim_" + filename + "_{}.pkl".format(N_cycles),
        )
    )
