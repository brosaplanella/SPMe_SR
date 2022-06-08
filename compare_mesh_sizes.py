#
# Get system size for different mesh sizes
#


import pybamm
import numpy as np
import pandas as pd
from auxiliary_functions import assemble_model, set_parameters, create_model_tag

pybamm.set_logging_level("WARNING")

factors = [1, 2, 4, 8]

# Define models
options = {"SEI": False, "plating": True, "porosity": True}
SPMe = assemble_model({"name": "SPMe+SR", **options})
DFN = assemble_model({"name": "DFN+SR", **options})

models = [SPMe, DFN]

param = set_parameters()

var = pybamm.standard_spatial_vars

df = pd.DataFrame()

i = 0
N = len(models) * len(factors) ** 2

for model in models:
    for factor_x in factors:
        for factor_r in factors:
            i += 1
            print(
                f"Running case {i} of {N}: {model.name}, factor_x = {factor_x},"
                + f" factor_r = {factor_r}"
            )
            var_pts = {
                var.x_n: 20 * factor_x,
                var.x_s: 20 * factor_x,
                var.x_p: 20 * factor_x,
                var.r_n: 20 * factor_r,
                var.r_p: 20 * factor_r,
            }
            sim = pybamm.Simulation(
                model,
                parameter_values=param,
                var_pts=var_pts,
            )

            sim.build()

            size_algebraic = np.size(sim.built_model.concatenated_algebraic)
            size_rhs = np.size(sim.built_model.concatenated_rhs)
            df = df.append(
                {
                    "Model": model.name,
                    "Nx": 20 * factor_x,
                    "Nr": 20 * factor_r,
                    "# rhs": size_rhs,
                    "# algebraic": size_algebraic,
                    "# total": size_algebraic + size_rhs,
                },
                ignore_index=True,
            )

_, tag = create_model_tag(SPMe)
filename = "system_size" + tag + ".csv"
df.to_csv(filename)
