import pybamm
import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from cycler import cycler
from auxiliary_functions import *

plt.style.use(["science", "vibrant"])

mode = "paper"
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
            "font.family": "sans-serif",
            "text.usetex": False,
            "font.size": 6,
            "axes.labelsize": 8,
        }
    )


def plot_cycling_voltage(sims, plot_at_cycles=None):
    # Compare cycling voltages vs time (multiple cycles)
    fig, axes = plt.subplots(1, 1, figsize=(2.8, 2))
    N = min([len(sim.solution.all_first_states) for sim in sims])

    if plot_at_cycles is None:
        cycle_list = [0, int(N / 2) - 1, N - 1]
    elif isinstance(plot_at_cycles, int):
        cycle_list = list(range(plot_at_cycles - 1, N, plot_at_cycles))
        cycle_list = [0] + cycle_list
        # if cycle_list[-1] < N - 1:
        #     cycle_list = cycle_list + [N - 1]
    else:
        cycle_list = plot_at_cycles

        # experiment = pybamm.Experiment(
        #     [sim.experiment.operating_conditions_cycles[0][0] + " (30 second period)"]
        # )
        # sim_cycle = run_cycle(sim, 0, experiment=experiment)

        # axes.plot(
        #     sim_cycle.solution["Discharge capacity [A.h]"].entries,
        #     sim_cycle.solution["Terminal voltage [V]"].entries,
        #     label=label,
        #     linestyle=linestyle,
        #     color=color,
        #     linewidth=linewidth,
        # )

    for i in cycle_list:
        for sim in sims:
            if sim.model.name[:3] == "DFN":
                linestyle = "-"
                color = "black"
                linewidth = 0.75
                if i == cycle_list[0]:
                    label = "DFN+SR"
                    # label = "Full model"
                else:
                    label = None
            else:
                linestyle = "--"
                color = None
                linewidth = None
                label = "SPMe+SR - Cycle {}".format(i + 1)
                # label = "Reduced model - Cycle {}".format(i + 1)

            print("{}: run cycle {}".format(sim.model.name[:3], i))
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
                label=label,
            )

    axes.set_xlabel("Discharge capacity [A.h]")
    axes.set_ylabel("Terminal voltage [V]")
    axes.legend()

    fig.tight_layout()

    return fig, axes


def plot_capacity(sims, filename, C_rates=[1 / 3, 1 / 2, 1]):
    # Compare theoretical & RPT capacity vs cycle number
    fig, axes = plt.subplots(1, 1, figsize=(2.8, 2))
    N = 0

    for sim in sims:
        if sim.model.name[:3] == "DFN":
            linestyle = "-"
            color = "black"
            linewidth = 0.75
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

def plot_capacity_single_plot(options, N_cycles=1000):
    # Compare theoretical & RPT capacity vs cycle number
    fig, axes = plt.subplots(2, 2, figsize=(5.5, 3.5), sharey=True, sharex=True)
    N = 0
    C_chs = [1 / 3, 1 / 2]
    C_dchs = [1, 2]
    # C_RPT = [1 / 3, 1 / 2, 1]
    C_RPT = [1 / 3]

    for i, C_dch in enumerate(C_dchs):
        for j, C_ch in enumerate(C_chs):

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

            Q0 = DFN.solution.summary_variables["Capacity [A.h]"][0]

            axes[j, i].plot(
                DFN.solution.summary_variables["Cycle number"][:],
                DFN.solution.summary_variables["Capacity [A.h]"][:],
                label="DFN+SR",
                linestyle="-",
                color="black",
                linewidth=0.75,
            )

            axes[j, i].plot(
                SPMe.solution.summary_variables["Cycle number"][:],
                SPMe.solution.summary_variables["Capacity [A.h]"][:],
                label="SPMe+SR - theor.",
                linestyle="--"
            )

            N = max([
                N, 
                SPMe.solution.summary_variables["Cycle number"][-1],
                DFN.solution.summary_variables["Cycle number"][-1],
            ])

            for C_rate in C_RPT:
                SPMe = pd.read_csv(
                    os.path.join(
                        "data",
                        "RPT_"
                        + create_C_tag(C_rate)
                        + "_"
                        + create_filename({"name": "SPMe_SR", **options}, C_dch, C_ch)
                        + "_{}.csv".format(N_cycles),
                    )
                )

                DFN = pd.read_csv(
                    os.path.join(
                        "data",
                        "RPT_"
                        + create_C_tag(C_rate)
                        + "_"
                        + create_filename({"name": "DFN_SR", **options}, C_dch, C_ch)
                        + "_{}.csv".format(N_cycles),
                    )
                )

                axes[j, i].plot(
                    DFN["Cycle number"],
                    DFN["Discharge capacity [A.h]"],
                    label=None,
                    linestyle="-",
                    color="black",
                    linewidth=0.75,
                )

                axes[j, i].plot(
                    SPMe["Cycle number"],
                    SPMe["Discharge capacity [A.h]"],
                    label="SPMe+SR - RPT " + create_C_tag(C_rate, True),
                    linestyle="--",
                )

    def abs2rel(x):
        return x / Q0 * 100

    def rel2abs(x):
        return x * Q0 / 100

    for i in range(2):
        for j in range(2):
            axes[i, j].set_xlim([1, N])
        axes[1, i].set_xlabel("Cycle number")
        axes[i, 0].set_ylabel("Capacity [A.h]")
        secax = axes[i, 1].secondary_yaxis('right', functions=(abs2rel, rel2abs))
        secax.set_ylabel('Rel. capacity [%]')

    pad = 5  # in points

    for ax, col in zip(axes[0], C_dchs):
        ax.annotate(
            create_C_tag(col, True) + " discharge",
            xy=(0.5, 1),
            xytext=(0, pad),
            xycoords="axes fraction",
            textcoords="offset points",
            size="large",
            ha="center",
            va="baseline",
        )

    for ax, row in zip(axes[:, 0], C_chs):
        ax.annotate(
            create_C_tag(row, True) + " charge",
            xy=(0, 0.5),
            xytext=(-ax.yaxis.labelpad - pad, 0),
            xycoords=ax.yaxis.label,
            textcoords="offset points",
            size="large",
            ha="right",
            va="center",
            rotation=90,
        )
    
    axes[0, 0].legend()
    # handles, labels = axes[0, 0].get_legend_handles_labels()
    # fig.legend(handles, labels, loc='lower center')

    fig.tight_layout()

    return fig, axes

def plot_average_porosity(sims):
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
    axes.set_ylabel("Averaged porosity")
    axes.legend()
    axes.set_xlim([1, N])

    return fig, axes

def plot_average_porosity_single_plot(options, N_cycles=1000):
    # Compare average thickness/porosity vs cycle number
    fig, axes = plt.subplots(1, 1, figsize=(2.8, 2))
    N = 0
    C_chs = [1 / 3, 1 / 2]
    C_dchs = [1, 2]

    count = 0

    for C_dch in C_dchs:
        for C_ch in C_chs:

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

            for sim in sims:
                if sim.model.name[:3] == "DFN":
                    if count == 0:
                        label = "DFN+SR"
                    else:
                        label = None
                    linestyle = "-"
                    color = "black"
                    linewidth = 0.75
                else:
                    linestyle = "--"
                    color = None
                    linewidth = None
                    label = "SPMe+SR - " + create_C_tag(C_ch, True) + " ch, " + create_C_tag(C_dch, True) + " dch"

                porosity = []
                for sol in sim.solution.all_first_states:
                    porosity.append(sol["X-averaged negative electrode porosity"].entries[0])

                axes.plot(
                    range(1, len(porosity) + 1),
                    porosity,
                    label=label,
                    linestyle=linestyle,
                    color=color,
                    linewidth=linewidth,
                )

                N = max(N, len(porosity))
            
            count += 1

    axes.set_xlabel("Cycle number")
    axes.set_ylabel("Averaged porosity")
    axes.legend()
    axes.set_xlim([1, N])

    fig.tight_layout()

    return fig, axes

def plot_porosity_distribution(sims, plot_at_cycles=None):
    # Compare thickness/porosity at different cycle numbers
    fig, axes = plt.subplots(1, 1, figsize=(2.8, 2))
    N = min([len(sim.solution.all_first_states) for sim in sims])

    if plot_at_cycles is None:
        cycle_list = list(range(N))
    elif isinstance(plot_at_cycles, int):
        cycle_list = list(range(plot_at_cycles - 1, N, plot_at_cycles))
        cycle_list = [0] + cycle_list
        # if cycle_list[-1] < N - 1:
        #     cycle_list = cycle_list + [N - 1]

    else:
        cycle_list = plot_at_cycles

    for sim in sims:
        if sim.model.name[:3] == "DFN":
            linestyle = "-"
            color = "black"
            linewidth = 1
        else:
            linestyle = "--"
            color = None
            linewidth = None

        for cycle in cycle_list:
            if cycle == cycle_list[0]:
                if sim.model.name[:3] == "DFN":
                    # label = "Full model"
                    label = "DFN+SR"
                else:
                    # label = "Reduced model"
                    label="SPMe+SR"
            else:
                label = None


            sol = sim.solution.all_first_states[cycle]
            porosity = sol["Negative electrode porosity"].entries
            x = sol["x_n [m]"].entries

            axes.plot(
                x,
                porosity,
                label=label,
                linestyle=linestyle,
                color=color,
                linewidth=linewidth,
            )

            if sim.model.name[:3] == "SPM":
                axes.text(x[-1] * 1.02, porosity[-1], 'Cycle {}'.format(cycle + 1))

    axes.set_xlabel("x [m]")
    axes.set_ylabel("Negative electrode porosity")
    axes.set_xlim([0, x[-1]])
    axes.legend()

    fig.tight_layout()

    return fig, axes

if __name__ == "__main__":
    N_cycles = 1000
    # C_chs = [1 / 3, 1 / 2]
    C_chs = [1 / 2]
    # C_dchs = [1, 2]
    C_dchs = [1]

    options_list = [
        # {"SEI": True, "plating": False, "porosity": True},
        {"SEI": False, "plating": True, "porosity": True},
        # {"SEI": True, "plating": True, "porosity": True},
    ]

    for options in options_list:
        _, submodel_tag = create_model_tag({"name": "SPMe_SR", **options})
        # fig, axes = plot_capacity_single_plot(options)
        # fig.savefig(
        #     os.path.join("figures", "compare_capacity" + submodel_tag + "_{}.png".format(N_cycles)),
        #     dpi=300,
        # )

        # fig, axes = plot_average_porosity_single_plot(options)
        # fig.savefig(
        #     os.path.join("figures", "compare_average_porosity" + submodel_tag + "_{}.png".format(N_cycles)),
        #     dpi=300,
        # )
        # plt.show()

        for C_ch in C_chs:
            for C_dch in C_dchs:


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

                # save_filename = save_filename + "_poster"

                fig, axes = plot_cycling_voltage(sims)
                fig.savefig(
                    os.path.join("figures", "compare_voltage" + save_filename + ".png"),
                    dpi=300,
                )

                fig, axes = plot_capacity(
                    sims,
                    save_filename,
                )
                fig.savefig(
                    os.path.join("figures", "compare_capacity" + save_filename + ".png"),
                    dpi=300,
                )

        #         fig, axes = plot_porosity(sims)
        #         fig.savefig(
        #             os.path.join("figures", "compare_average_porosity" + save_filename + ".png"), 
        #             dpi=300,
        #         )

                fig, axes = plot_porosity_distribution(sims, plot_at_cycles=100)
                fig.savefig(
                    os.path.join("figures", "compare_porosity" + save_filename + ".png"), 
                    dpi=300,
                )

                # plt.show()
