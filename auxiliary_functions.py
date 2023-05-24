#
# Define auxiliary functions to run the scripts
#

import pybamm
import pandas as pd
import matplotlib.pyplot as plt
import gc
import scienceplots


def set_plotting_format(mode="presentation"):
    plt.style.use(["science", "vibrant"])

    mode = "paper"

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

    elif mode == "paper":
        plt.rcParams.update(
            {
                "font.family": "sans-serif",
                "text.usetex": False,
                "font.size": 6,
                "axes.labelsize": 8,
            }
        )


def create_filename(model, C_dch, C_ch):
    model_name, tag = create_model_tag(model)

    if isinstance(C_dch, str):
        dch_tag = C_dch
    else:
        dch_tag = create_C_tag(C_dch)

    filename = model_name + "_" + dch_tag + "_" + create_C_tag(C_ch)
    filename = filename.replace("+", "_") + tag
    return filename


def run_cycle(simulation, cycle_number, experiment=None):
    # set initial conditions
    model = simulation.model
    model.set_initial_conditions_from(
        simulation.solution.all_first_states[cycle_number]
    )

    if experiment is None:
        experiment = pybamm.Experiment(
            simulation.experiment.operating_conditions_cycles[cycle_number]
        )

    # solve cycle
    sim = pybamm.Simulation(
        model,
        experiment=experiment,
        parameter_values=simulation.parameter_values,
        var_pts=simulation.var_pts,
        # solver=simulation.solver,
    )
    sim.solve()

    return sim


def create_C_tag(C_rate, bar=False):
    if float(C_rate).is_integer():
        C_tag = "{:.0f}C".format(C_rate)
    elif float(1 / C_rate).is_integer():
        C_tag = "C{:.0f}".format(1 / C_rate)
    else:
        C_tag = "{:.2f}C".format(C_rate)

    if bar and C_tag[0] == "C":
        C_tag = C_tag[0] + "/" + C_tag[1:]

    return C_tag


def create_model_tag(model):
    tag = ""

    if isinstance(model, pybamm.BaseModel):
        model_name = model.name
        if not isinstance(model.submodels["primary sei"], pybamm.sei.NoSEI):
            tag += "_SEI"
        if not isinstance(
            model.submodels["lithium plating"], pybamm.lithium_plating.NoPlating
        ):
            tag += "_plating"
        if not isinstance(model.submodels["porosity"], pybamm.porosity.Constant):
            tag += "_porosity"
    else:
        model_name = model["name"]
        if model["SEI"]:
            tag += "_SEI"
        if model["plating"]:
            tag += "_plating"
        if model["porosity"]:
            tag += "_porosity"

    return model_name, tag


def assemble_model(options):
    raise NotImplementedError(
        "The assemble_model has been deprecated,"
        " please define the model using PyBaMM options"
    )


def stripping_exchange_current_density_OKane2020(c_e, c_Li, T):
    """
    Exchange-current density for Li stripping reaction [A.m-2].
    References
    ----------
    .. [1] O’Kane, Simon EJ, Ian D. Campbell, Mohamed WJ Marzook, Gregory J. Offer, and
    Monica Marinescu. "Physical origin of the differential voltage minimum associated
    with lithium plating in Li-ion batteries." Journal of The Electrochemical Society
    167, no. 9 (2020): 090540.
    Parameters
    ----------
    c_e : :class:`pybamm.Symbol`
        Electrolyte concentration [mol.m-3]
    c_Li : :class:`pybamm.Symbol`
        Plated lithium concentration [mol.m-3]
    T : :class:`pybamm.Symbol`
        Temperature [K]
    Returns
    -------
    :class:`pybamm.Symbol`
        Exchange-current density [A.m-2]
    """

    k_plating = pybamm.Parameter("Lithium plating kinetic rate constant [m.s-1]")

    return pybamm.constants.F * k_plating * c_Li


def plating_exchange_current_density_OKane2020(c_e, c_Li, T):
    """
    Exchange-current density for Li plating reaction [A.m-2].
    References
    ----------
    .. [1] O’Kane, Simon EJ, Ian D. Campbell, Mohamed WJ Marzook, Gregory J. Offer, and
    Monica Marinescu. "Physical origin of the differential voltage minimum associated
    with lithium plating in Li-ion batteries." Journal of The Electrochemical Society
    167, no. 9 (2020): 090540.
    Parameters
    ----------
    c_e : :class:`pybamm.Symbol`
        Electrolyte concentration [mol.m-3]
    c_Li : :class:`pybamm.Symbol`
        Plated lithium concentration [mol.m-3]
    T : :class:`pybamm.Symbol`
        Temperature [K]
    Returns
    -------
    :class:`pybamm.Symbol`
        Exchange-current density [A.m-2]
    """

    k_plating = pybamm.Parameter("Lithium plating kinetic rate constant [m.s-1]")

    return pybamm.constants.F * k_plating * c_e


def set_parameters(ref="Chen2020"):
    param = pybamm.ParameterValues(ref)

    param.update(
        {
            "EC diffusivity [m2.s-1]": 2e-19,
            "Inner SEI partial molar volume [m3.mol-1]": 0.162 / 1690,
            "Outer SEI partial molar volume [m3.mol-1]": 0.162 / 1690,
            "SEI resistivity [Ohm.m]": 2e5,
            "Initial inner SEI thickness [m]": 0,
            "Initial outer SEI thickness [m]": 5e-9,
            "EC initial concentration in electrolyte [mol.m-3]": 4541,
            "SEI kinetic rate constant [m.s-1]": 1e-12,
            "SEI open-circuit potential [V]": 0,
            "Lithium plating kinetic rate constant [m.s-1]": 1e-11,
            "SEI growth transfer coefficient": 0.5,
            "Lithium metal partial molar volume [m3.mol-1]": 1.30e-05,
            "Exchange-current density for plating [A.m-2]"
            "": plating_exchange_current_density_OKane2020,
            "Exchange-current density for stripping [A.m-2]"
            "": stripping_exchange_current_density_OKane2020,
            "Initial plated lithium concentration [mol.m-3]": 0.00e00,
            "Typical plated lithium concentration [mol.m-3]": 1000,
            "Lithium plating transfer coefficient": 0.5,
        },
        check_already_exists=False,
    )

    return param


def run_RPT(simulation, C_rate=1 / 3, RPT_at_cycles=None):
    """Runs RPT for a given simulation and C_rate."""

    experiment = pybamm.Experiment(["Discharge at {}C until 2.5V".format(C_rate)])

    capacity = []
    termination = []
    N = len(simulation.solution.all_first_states)

    if RPT_at_cycles is None:
        cycle_list = list(range(N))
    elif isinstance(RPT_at_cycles, int):
        cycle_list = list(range(RPT_at_cycles - 1, N, RPT_at_cycles))
        cycle_list = [0] + cycle_list
    else:
        cycle_list = RPT_at_cycles

    for i in cycle_list:
        # print output
        print("Running RPT for cycle {} of {}".format(i + 1, N))

        # set initial conditions
        model = simulation.model
        model.set_initial_conditions_from(simulation.solution.all_first_states[i])

        # solve cycle
        if experiment is not None:
            sim = pybamm.Simulation(
                model,
                experiment=experiment,
                parameter_values=simulation.parameter_values,
                solver=simulation.solver,
                var_pts=simulation.var_pts,
            )
        sim.solve()
        capacity.append(sim.solution["Discharge capacity [A.h]"].entries[-1])
        termination.append(sim.solution.termination)

        del model
        del sim
        gc.collect()

    df = pd.DataFrame(
        data={
            "Cycle number": [x + 1 for x in cycle_list],
            "Discharge capacity [A.h]": capacity,
            "Termination": termination,
        }
    )

    return df
