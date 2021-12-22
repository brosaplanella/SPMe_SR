import pybamm
import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from cycler import cycler
from auxiliary_functions import create_filename, run_cycle, create_C_tag

plt.style.use(["science", "vibrant"])

mode = "presentation"
save_plots = True

if mode == "presentation":
    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "text.usetex": False,
            "font.size": 10,
            "axes.labelsize": 12,
            "lines.linewidth": 2,
        }
    )
    # plt.rcParams["axes.prop_cycle"] += cycler("linestyle", ['-', '--', ':', '-.'])


elif mode == "paper":
    plt.rcParams.update(
        {
            "font.size": 8,
            "axes.labelsize": 10,
        }
    )


def plot_cycling_voltage(sims, cycles_plot=100):
    # Compare cycling voltages vs time (multiple cycles)
    fig, axes = plt.subplots(1, 1, figsize=(7.5, 5))
    N = min([len(sim.solution.all_first_states) for sim in sims])
    if isinstance(cycles_plot, list):
        _cycles_plot = cycles_plot
    else:
        _cycles_plot = list(range(cycles_plot - 1, N, cycles_plot))

    for sim in sims:
        if sim.model.name[:3] == "DFN":
            linestyle = "-"
            color = "black"
            linewidth = 1
            label = "DFN+SR"
        else:
            linestyle = "--"
            color = "C0"
            linewidth = None
            label = "SPMe+SR"

        experiment = pybamm.Experiment(
            [sim.experiment.operating_conditions_cycles[0][0] + " (30 second period)"]
        )
        sim_cycle = run_cycle(sim, 0, experiment=experiment)

        axes.plot(
            sim_cycle.solution["Discharge capacity [A.h]"].entries,
            sim_cycle.solution["Terminal voltage [V]"].entries,
            label=label,
            linestyle=linestyle,
            color=color,
            linewidth=linewidth,
        )

        for i in _cycles_plot:
            print("{}: run cycle {}".format(label, i))
            experiment = pybamm.Experiment(
                [
                    sim.experiment.operating_conditions_cycles[i][0]
                    + " (30 second period)"
                ]
            )
            sim_cycle = run_cycle(sim, i, experiment=experiment)
            axes.plot(
                sim_cycle.solution["Discharge capacity [A.h]"].entries,
                sim_cycle.solution["Terminal voltage [V]"].entries,
                linestyle=linestyle,
                color=color,
                linewidth=linewidth,
            )

    axes.set_xlabel("Discharge capacity [A.h]")
    axes.set_ylabel("Terminal voltage [V]")
    axes.legend()

    return fig, axes


def plot_capacity(sims, filename, C_rates=[1 / 3, 1 / 2, 1]):
    # Compare theoretical & RPT capacity vs cycle number
    fig, axes = plt.subplots(1, 1, figsize=(7.5, 5))
    N = 0

    for sim in sims:
        if sim.model.name[:3] == "DFN":
            linestyle = "-"
            color = "black"
            linewidth = 1
            label = "DFN+SR"
        else:
            linestyle = "--"
            color = None
            linewidth = None
            label = "SPMe+SR - theoretical"

        axes.plot(
            sim.solution.summary_variables["Cycle number"][:],
            sim.solution.summary_variables["Capacity [A.h]"][:],
            label=label,
            linestyle=linestyle,
            color=color,
            linewidth=linewidth,
        )

        # axes.plot(
        #     sim.solution.summary_variables["Cycle number"][:],
        #     sim.solution.summary_variables["Measured capacity [A.h]"][:],
        #     label=sim.model.name + " - cycle",
        # )

        N = max(N, sim.solution.summary_variables["Cycle number"][-1])

        for C_rate in C_rates:
            if sim.model.name[:3] == "DFN":
                label = None
            else:
                label = "SPMe+SR - RPT {:.2f}C".format(C_rate)

            path = os.path.join(
                "data",
                "RPT_"
                + create_C_tag(C_rate)
                + "_"
                + sim.model.name.replace("+", "_")
                + filename
                + ".csv",
            )
            data = pd.read_csv(path)
            axes.plot(
                data["Cycle number"],
                data["Discharge capacity [A.h]"],
                label=label,
                linestyle=linestyle,
                color=color,
                linewidth=linewidth,
            )

    axes.set_xlabel("Cycle number")
    axes.set_ylabel("Capacity [A.h]")
    axes.legend()
    axes.set_xlim([1, N])

    return fig, axes


def plot_porosity(sims):
    # Compare average thickness/porosity vs cycle number
    fig, axes = plt.subplots(1, 1, figsize=(7.5, 5))
    N = 0

    for sim in sims:
        if sim.model.name[:3] == "DFN":
            linestyle = "-"
            color = "black"
            linewidth = 1
        else:
            linestyle = "--"
            color = None
            linewidth = None

        porosity = []
        for sol in sim.solution.all_first_states:
            porosity.append(sol["X-averaged negative electrode porosity"].entries[0])

        axes.plot(
            range(1, len(porosity) + 1),
            porosity,
            label=sim.model.name,
            linestyle=linestyle,
            color=color,
            linewidth=linewidth,
        )

        N = max(N, len(porosity))

    axes.set_xlabel("Cycle number")
    axes.set_ylabel("X-averaged negative electrode porosity")
    axes.legend()
    axes.set_xlim([1, N])

    return fig, axes

    pass


if __name__ == "__main__":
    N_cycles = 1000
    C_ch = 1 / 3
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

    sims = [DFN, SPMe]

    save_filename = create_filename({"name": "", **options}, C_dch, C_ch) + "_{}".format(N_cycles)

    # fig, axes = plot_cycling_voltage(sims)
    # fig.savefig(
    #     os.path.join("figures", "compare_voltage_" + save_filename + ".png"),
    #     dpi=300,
    # )

    fig, axes = plot_capacity(
        sims,
        save_filename,
    )
    fig.savefig(
        os.path.join("figures", "compare_capacity" + save_filename + ".png"),
        dpi=300,
    )

    fig, axes = plot_porosity(sims)
    fig.savefig(
        os.path.join("figures", "compare_porosity" + save_filename + ".png"), 
        dpi=300,
    )

    plt.show()
