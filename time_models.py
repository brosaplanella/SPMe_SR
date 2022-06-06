#
# Get computational time DFN+SR and SPMe+SR
#

from multiprocessing.sharedctypes import Value
import pybamm
import numpy as np
from prettytable import PrettyTable
from auxiliary_functions import *

pybamm.set_logging_level("WARNING")

# Define models
options = {"SEI": True, "plating": True, "porosity": True}
SPMe = assemble_model({"name": "SPMe+SR", **options})
DFN = assemble_model({"name": "DFN+SR", **options})

models = [SPMe, DFN]

solvers = {
    # pybamm.ScipySolver(),
    pybamm.ScikitsOdeSolver(),
    pybamm.ScikitsDaeSolver(),
    # pybamm.CasadiSolver("fast with events"),
    # pybamm.CasadiSolver("fast with events"),
}

# Define parameters
param = set_parameters()

# Change simulation parameters here
N_solve = 2  # number of times to run the solver to get computational time
N_cycles = 10
C_ch = 1 / 2
C_dch = 1
factors_x = [1, 2]
factors_r = [1, 2]
solver_types = ["casadi", "scikits"]
modes = {
    "CC": C_dch,
    # "CCCV": pybamm.Experiment(
    #     [
    #         (
    #             "Discharge at {}C until 2.5 V".format(C_dch),
    #             "Charge at {}C until 4.2 V".format(C_ch),
    #             "Hold at 4.2 V until C/20",
    #         )
    #     ]
    #     * N_cycles,
    # ),
}

tables = []
var = pybamm.standard_spatial_vars

for solver_type in solver_types:
    for mode_name, mode_settings in modes.items():
        print(f"{mode_name} simulation with {solver_type} solvers")
        table = PrettyTable(
            [mode_name + " & " + solver_type] + [model.name for model in models]
        )

        for factor_x in factors_x:
            for factor_r in factors_r:
                times = []
                for model in models:
                    print(f"Running {model.name} for Nx={20 * factor_x} and Nr={20 *factor_r}")
                    
                    # Define number of points in mesh
                    var_pts = {
                        var.x_n: 20 * factor_x,
                        var.x_s: 20 * factor_x,
                        var.x_p: 20 * factor_x,
                        var.r_n: 20 * factor_r,
                        var.r_p: 20 * factor_r,
                    }

                    # Define operating mode
                    if solver_type not in ["casadi", "scikits"]:
                        raise ValueError(f"Solver type {solver_type} not recognised. Should be either 'casadi' or 'scikits'")
                    
                    if solver_type == "casadi":
                        solver = pybamm.CasadiSolver("safe")

                    if isinstance(mode_settings, pybamm.Experiment):
                        C_rate = None
                        experiment = mode_settings
                        t_eval = None
                        if solver_type == "scikits":
                            solver = pybamm.ScikitsDaeSolver()
                    elif isinstance(mode_settings, (int, float)):
                        C_rate = mode_settings
                        experiment = None
                        t_eval = [0, 4000 / C_rate]
                        if solver_type == "scikits":
                            solver = pybamm.ScikitsOdeSolver()
                    else:
                        raise ValueError(f"Mode settings not recognised. Should be either a number or a pybamm.Experiment")

                    sim = pybamm.Simulation(
                        model,
                        parameter_values=param,
                        experiment=experiment,
                        C_rate=C_rate,
                        var_pts=var_pts,
                        solver=solver,
                    )

                    time_sublist = []
                    for j in range(N_solve):
                        print(f"Solving case {j + 1} out of {N_solve}")
                        sim.solve(t_eval, calc_esoh=False)
                        time_sublist.append(sim.solution.solve_time.value)

                    times.append(time_sublist)

                    table.add_row(
                        [f"Nx = {20 * factor_x}, Nr = {20 * factor_r}"]
                        + ["{:.2f} +- {:.2f}".format(np.mean(time), np.std(time)) for time in times]
                    )

        tables.append([table, [mode_name, solver_type]])
        print(table)

print()
print("Summary results:")

for table_info in tables:
    print()
    print(f"{table_info[1][0]} simulation with {table_info[1][1]} solvers")
    print(table_info[0])
