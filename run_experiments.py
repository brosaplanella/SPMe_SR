import os
import pybamm
from auxiliary_functions import assemble_model, set_parameters, create_filename

pybamm.set_logging_level("INFO")

# Define models
options = {"SEI": True, "plating": True, "porosity": True}
SPMe = assemble_model({"name": "SPMe+SR", **options})
DFN = assemble_model({"name": "DFN+SR", **options})

models = [SPMe, DFN]

# Define parameters
param = set_parameters()

# Define experiment
N_cycles = 1000
save_at_cycles = [1]    # [1] by default to save memory
C_ch = 1 / 3
C_dch = 2

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
    sim.save(
        os.path.join(
            "data",
            "sim_" + filename + "_{}.pkl".format(N_cycles),
        )
    )
