import pybamm
import os
import gc
from auxiliary_functions import (
    create_filename,
    run_RPT,
    set_plotting_format,
    create_C_tag,
)

# Define plotting format
set_plotting_format()

# Define model options
N_cycles = 1000
C_ch = 1 / 2
C_dch = 1
options = {"SEI": True, "plating": True, "porosity": True}
RPT_at_cycles = 10
sims = ["SPMe_SR", "DFN_SR"]
C_rates = [1 / 3]

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
        df = run_RPT(sim, C_rate=C_rate, RPT_at_cycles=RPT_at_cycles)

        df.to_csv(
            os.path.join(
                "data",
                "RPT"
                + create_C_tag(C_rate)
                + "_"
                + create_filename(sim.model, C_dch, C_ch)
                + "_{}.csv".format(N_cycles),
            )
        )

        gc.collect()
