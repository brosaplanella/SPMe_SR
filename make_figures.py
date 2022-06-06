#
# Generate figures for the article
#

import pybamm
import os
import matplotlib.pyplot as plt
import pandas as pd
from auxiliary_functions import (
    set_plotting_format,
    create_C_tag,
    create_filename,
    run_cycle,
    create_model_tag,
)

# Define plotting format
set_plotting_format()


def plot_capacity_single_plot(options, N_cycles=1000):
    # Compare theoretical & RPT capacity vs cycle number
    fig, axes = plt.subplots(2, 2, figsize=(5.5, 3.5), sharey=True, sharex=True)
    N = 0
    C_chs = [1 / 3, 1 / 2]
    C_dchs = [1, 2]
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
                linestyle="--",
            )

            N = max(
                [
                    N,
                    SPMe.solution.summary_variables["Cycle number"][-1],
                    DFN.solution.summary_variables["Cycle number"][-1],
                ]
            )

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
        secax = axes[i, 1].secondary_yaxis("right", functions=(abs2rel, rel2abs))
        secax.set_ylabel("Rel. capacity [%]")

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

    axes[-1, -1].legend()

    fig.tight_layout()

    return fig, axes


def plot_porosity_single_plot(options, N_cycles=1000, plot_at_cycles=None):
    # Compare porosity distribution vs space and time
    fig, axes = plt.subplots(2, 2, figsize=(5.5, 3.5), sharey=True, sharex=True)
    C_chs = [1 / 3, 1 / 2]
    C_dchs = [1, 2]

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

            sims = [DFN, SPMe]
            ax = axes[j, i]

            N = min([len(sim.solution.all_first_states) for sim in sims])

            if plot_at_cycles is None:
                cycle_list = list(range(N))
            elif isinstance(plot_at_cycles, int):
                cycle_list = list(range(plot_at_cycles - 1, N, plot_at_cycles))
                cycle_list = [0] + cycle_list
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
                            label = "DFN+SR"
                        else:
                            label = "SPMe+SR"
                    else:
                        label = None

                    sol = sim.solution.all_first_states[cycle]
                    porosity = sol["Negative electrode porosity"].entries
                    x = sol["x_n [m]"].entries

                    ax.plot(
                        x,
                        porosity,
                        label=label,
                        linestyle=linestyle,
                        color=color,
                        linewidth=linewidth,
                    )

                    if sim.model.name[:3] == "SPM":
                        ax.text(
                            x[-1] * 1.02, porosity[-1], "Cycle {}".format(cycle + 1)
                        )

                    ax.set_xlim([0, x[-1]])

    for i in range(2):
        axes[1, i].set_xlabel("x [m]")
        axes[i, 0].set_ylabel("Porosity")

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

    axes[-1, -1].legend()

    fig.tight_layout()

    return fig, axes


def plot_voltage_single_plot(options, N_cycles=1000, plot_at_cycles=None):
    # Compare voltage vs discharge capacity
    fig, axes = plt.subplots(2, 2, figsize=(5.5, 3.5), sharey=True, sharex=True)
    C_chs = [1 / 3, 1 / 2]
    C_dchs = [1, 2]

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

            sims = [DFN, SPMe]
            ax = axes[j, i]

            N = min([len(sim.solution.all_first_states) for sim in sims])

            if plot_at_cycles is None:
                cycle_list = [0, int(N / 2) - 1, N - 1]
            elif isinstance(plot_at_cycles, int):
                cycle_list = list(range(plot_at_cycles - 1, N, plot_at_cycles))
                cycle_list = [0] + cycle_list
            else:
                cycle_list = plot_at_cycles

            for cycle in cycle_list:
                for sim in sims:
                    if sim.model.name[:3] == "DFN":
                        linestyle = "-"
                        color = "black"
                        linewidth = 0.75
                        if cycle == cycle_list[0]:
                            label = "DFN+SR"
                        else:
                            label = None
                    else:
                        linestyle = "--"
                        color = None
                        linewidth = None
                        label = "SPMe+SR - Cycle {}".format(cycle + 1)

                    print("{}: run cycle {}".format(sim.model.name[:3], cycle))
                    experiment = pybamm.Experiment(
                        [
                            sim.experiment.operating_conditions_cycles[cycle][0]
                            + " (30 second period)"
                        ]
                    )
                    sim_cycle = run_cycle(sim, cycle, experiment=experiment)
                    ax.plot(
                        sim_cycle.solution["Discharge capacity [A.h]"].entries,
                        sim_cycle.solution["Terminal voltage [V]"].entries,
                        linestyle=linestyle,
                        color=color,
                        linewidth=linewidth,
                        label=label,
                    )

                    ax.legend()

    for i in range(2):
        axes[1, i].set_xlabel("Discharge capacity [A.h]")
        axes[i, 0].set_ylabel("Terminal voltage [V]")

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

    axes[-1, -1].legend()

    fig.tight_layout()

    return fig, axes


def plot_capacity_across_models(C_dch=1, C_ch=0.5, N_cycles=1000):
    # Compare theoretical & RPT capacity vs cycle number
    fig, axes = plt.subplots(1, 3, figsize=(5.5, 2), sharey=True, sharex=True)
    N = 0
    C_RPT = [1 / 3]

    options_list = [
        {"SEI": True, "plating": False, "porosity": True},
        {"SEI": False, "plating": True, "porosity": True},
        {"SEI": True, "plating": True, "porosity": True},
    ]

    for ax, options in zip(axes, options_list):
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

        ax.plot(
            DFN.solution.summary_variables["Cycle number"][:],
            DFN.solution.summary_variables["Capacity [A.h]"][:],
            label="DFN+SR",
            linestyle="-",
            color="black",
            linewidth=0.75,
        )

        ax.plot(
            SPMe.solution.summary_variables["Cycle number"][:],
            SPMe.solution.summary_variables["Capacity [A.h]"][:],
            label="SPMe+SR - theor.",
            linestyle="--",
        )

        N = max(
            [
                N,
                SPMe.solution.summary_variables["Cycle number"][-1],
                DFN.solution.summary_variables["Cycle number"][-1],
            ]
        )

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

            ax.plot(
                DFN["Cycle number"],
                DFN["Discharge capacity [A.h]"],
                label=None,
                linestyle="-",
                color="black",
                linewidth=0.75,
            )

            if len(C_RPT) == 1:
                label = "SPMe+SR - RPT"
            else:
                label = "SPMe+SR - RPT " + create_C_tag(C_rate, True)

            ax.plot(
                SPMe["Cycle number"],
                SPMe["Discharge capacity [A.h]"],
                label=label,
                linestyle="--",
            )

    def abs2rel(x):
        return x / Q0 * 100

    def rel2abs(x):
        return x * Q0 / 100

    for ax in axes:
        ax.set_xlim([1, N])
        ax.set_xlabel("Cycle number")

    axes[0].set_ylabel("Capacity [A.h]")
    secax = axes[-1].secondary_yaxis("right", functions=(abs2rel, rel2abs))
    secax.set_ylabel("Rel. capacity [%]")

    pad = 5  # in points

    tags = [
        "SEI growth",
        "Lithium plating",
        "SEI growth + Lithium plating",
    ]

    for ax, tag in zip(axes, tags):
        ax.annotate(
            tag,
            xy=(0.5, 1),
            xytext=(0, pad),
            xycoords="axes fraction",
            textcoords="offset points",
            size="large",
            ha="center",
            va="baseline",
        )

    axes[-1].legend()

    fig.tight_layout()

    return fig, axes


def plot_porosity_across_models(C_dch=1, C_ch=0.5, N_cycles=1000, plot_at_cycles=100):
    # Compare porosity distribution vs space and time
    fig, axes = plt.subplots(1, 3, figsize=(5.5, 2), sharey=True, sharex=True)

    options_list = [
        {"SEI": True, "plating": False, "porosity": True},
        {"SEI": False, "plating": True, "porosity": True},
        {"SEI": True, "plating": True, "porosity": True},
    ]

    for ax, options in zip(axes, options_list):
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

        N = min([len(sim.solution.all_first_states) for sim in sims])

        if isinstance(plot_at_cycles, int):
            cycle_list = list(range(plot_at_cycles - 1, N, plot_at_cycles))
            cycle_list = [0] + cycle_list
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
                        label = "DFN+SR"
                    else:
                        label = "SPMe+SR"
                else:
                    label = None

                sol = sim.solution.all_first_states[cycle]
                porosity = sol["Negative electrode porosity"].entries
                x = sol["x_n [m]"].entries

                ax.plot(
                    x,
                    porosity,
                    label=label,
                    linestyle=linestyle,
                    color=color,
                    linewidth=linewidth,
                )

                if sim.model.name[:3] == "SPM" and cycle not in cycle_list[2:-1]:
                    ax.text(x[-1] * 1.02, porosity[-1], "Cycle {}".format(cycle + 1))

                ax.set_xlabel("x [m]")
                ax.set_xlim([0, x[-1]])

    pad = 5  # in points

    tags = [
        "SEI growth",
        "Lithium plating",
        "SEI growth + Lithium plating",
    ]

    for ax, tag in zip(axes, tags):
        ax.annotate(
            tag,
            xy=(0.5, 1),
            xytext=(0, pad),
            xycoords="axes fraction",
            textcoords="offset points",
            size="large",
            ha="center",
            va="baseline",
        )

    axes[0].set_ylabel("Porosity")

    axes[-1].legend()

    fig.tight_layout()

    return fig, axes


def plot_voltage_across_models(C_dch=1, C_ch=0.5, N_cycles=1000, plot_at_cycles=None):
    # Compare voltage vs discharge capacity
    fig, axes = plt.subplots(1, 3, figsize=(5.5, 2), sharey=True, sharex=True)

    options_list = [
        {"SEI": True, "plating": False, "porosity": True},
        {"SEI": False, "plating": True, "porosity": True},
        {"SEI": True, "plating": True, "porosity": True},
    ]

    for ax, options in zip(axes, options_list):
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

        N = min([len(sim.solution.all_first_states) for sim in sims])

        if plot_at_cycles is None:
            cycle_list = [0, int(N / 2) - 1, N - 1]
            cycle_tags = ["First", "Middle", "Last"]
        elif isinstance(plot_at_cycles, int):
            cycle_list = list(range(plot_at_cycles - 1, N, plot_at_cycles))
            cycle_list = [0] + cycle_list
            cycle_tags = [x + 1 for x in cycle_list]
        else:
            cycle_list = plot_at_cycles
            cycle_tags = [x + 1 for x in cycle_list]

        for sim in sims:
            if sim.model.name[:3] == "DFN":
                linestyle = "-"
                color = "black"
                linewidth = 1
            else:
                linestyle = "--"
                color = None
                linewidth = None

            for cycle, cycle_tag in zip(cycle_list, cycle_tags):
                if sim.model.name[:3] == "DFN":
                    linestyle = "-"
                    color = "black"
                    linewidth = 0.75
                    if cycle == cycle_list[0]:
                        label = "DFN+SR"
                    else:
                        label = None
                else:
                    linestyle = "--"
                    color = None
                    linewidth = None
                    label = "SPMe+SR - " + cycle_tag

                print("{}: run cycle {}".format(sim.model.name[:3], cycle))
                experiment = pybamm.Experiment(
                    [
                        sim.experiment.operating_conditions_cycles[cycle][0]
                        + " (30 second period)"
                    ]
                )
                sim_cycle = run_cycle(sim, cycle, experiment=experiment)
                ax.plot(
                    sim_cycle.solution["Discharge capacity [A.h]"].entries,
                    sim_cycle.solution["Terminal voltage [V]"].entries,
                    linestyle=linestyle,
                    color=color,
                    linewidth=linewidth,
                    label=label,
                )
                ax.set_xlabel("Discharge capacity [A.h]")

    pad = 5  # in points

    tags = [
        "SEI growth",
        "Lithium plating",
        "SEI growth + Lithium plating",
    ]

    for ax, tag in zip(axes, tags):
        ax.annotate(
            tag,
            xy=(0.5, 1),
            xytext=(0, pad),
            xycoords="axes fraction",
            textcoords="offset points",
            size="large",
            ha="center",
            va="baseline",
        )

    axes[0].set_ylabel("Terminal voltage [V]")

    axes[0].legend()

    fig.tight_layout()

    return fig, axes


if __name__ == "__main__":
    N_cycles = 1000
    C_chs = [1 / 3, 1 / 2]
    C_dchs = [1, 2]

    options_list = [
        {"SEI": True, "plating": False, "porosity": True},
        {"SEI": False, "plating": True, "porosity": True},
        {"SEI": True, "plating": True, "porosity": True},
    ]

    [fig, ax] = plot_capacity_across_models()
    fig.savefig(
        os.path.join("figures", "compare_capacity.png"),
        dpi=300,
    )

    [fig, ax] = plot_porosity_across_models()
    fig.savefig(
        os.path.join("figures", "compare_porosity.png"),
        dpi=300,
    )

    [fig, ax] = plot_voltage_across_models()
    fig.savefig(
        os.path.join("figures", "compare_voltage.png"),
        dpi=300,
    )

    for options in options_list:
        _, submodel_tag = create_model_tag({"name": "SPMe_SR", **options})
        fig, axes = plot_capacity_single_plot(options)
        fig.savefig(
            os.path.join(
                "figures",
                "compare_capacity" + submodel_tag + "_{}.png".format(N_cycles),
            ),
            dpi=300,
        )

        fig, axes = plot_porosity_single_plot(options, plot_at_cycles=100)
        fig.savefig(
            os.path.join(
                "figures",
                "compare_porosity" + submodel_tag + "_{}.png".format(N_cycles),
            ),
            dpi=300,
        )

        fig, axes = plot_voltage_single_plot(options)
        fig.savefig(
            os.path.join(
                "figures", "compare_voltage" + submodel_tag + "_{}.png".format(N_cycles)
            ),
            dpi=300,
        )

    # plt.show()
