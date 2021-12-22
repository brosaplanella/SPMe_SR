import pybamm
import pandas as pd


def create_filename(model, C_dch, C_ch):
    tag = ""
    if isinstance(model, pybamm.BaseModel):
        model_name = model.name
        if not isinstance(model.submodels["sei"], pybamm.sei.NoSEI):
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
        # solver=simulation.solver,
    )
    sim.solve()

    return sim


def create_C_tag(C_rate):
    if float(C_rate).is_integer():
        C_tag = "{:.0f}C".format(C_rate)
    elif float(1 / C_rate).is_integer():
        C_tag = "C{:.0f}".format(1 / C_rate)
    else:
        C_tag = "{:.2f}C".format(C_rate)

    return C_tag


def assemble_model(options):
    if options["name"].startswith("SPMe"):
        model = pybamm.lithium_ion.SPMe(build=False, name=options["name"])
        model.submodels[
            "electrolyte conductivity"
        ] = pybamm.electrolyte_conductivity.Integrated(model.param)
    elif options["name"].startswith("DFN"):
        model = pybamm.lithium_ion.DFN(build=False, name="DFN+SR")

    if options["SEI"]:
        model.submodels["sei"] = pybamm.sei.SEIGrowth(
            model.param, "full electrode", options={"SEI": "ec reaction limited"}
        )
    if options["plating"]:
        model.submodels["lithium plating"] = pybamm.lithium_plating.Plating(
            model.param, False, options={"lithium plating": "irreversible"}
        )
    if options["porosity"]:
        model.submodels["porosity"] = pybamm.porosity.ReactionDriven(
            model.param, model.options, False
        )

    model.build_model()

    return model

def set_parameters():
    chemistry = pybamm.parameter_sets.Chen2020
    chemistry.update({"lithium plating": "okane2020_Li_plating"})
    param = pybamm.ParameterValues(chemistry=chemistry)

    param.update(
        {
            "EC diffusivity [m2.s-1]": 2.5e-20,
            "Inner SEI partial molar volume [m3.mol-1]": 0.162 / 1690,
            "Outer SEI partial molar volume [m3.mol-1]": 0.162 / 1690,
            "SEI resistivity [Ohm.m]": 2e5,
            "Initial inner SEI thickness [m]": 0,
            "Initial outer SEI thickness [m]": 5e-9,
            "EC initial concentration in electrolyte [mol.m-3]": 4541,
            "SEI kinetic rate constant [m.s-1]": 1e-4,
            "SEI open-circuit potential [V]": 0.8,
            "Lithium plating kinetic rate constant [m.s-1]": 1e-11,
        }
    )

    return param

def run_RPT(simulation, experiment=None, C_rate=None):
    # Add argument for how many/which cycles to run

    if experiment is None:
        experiment = pybamm.Experiment(["Discharge at C/3 until 2.5V"])

    capacity = []
    termination = []
    N = len(simulation.solution.all_first_states)

    for i, first_state in enumerate(simulation.solution.all_first_states):
        # print output
        print("Running RPT {} of {}".format(i + 1, N))

        # set initial conditions
        model = simulation.model
        model.set_initial_conditions_from(first_state)

        # solve cycle
        if experiment is not None:
            sim = pybamm.Simulation(
                model,
                experiment=experiment,
                parameter_values=simulation.parameter_values,
                solver=simulation.solver,
            )
        sim.solve()
        capacity.append(sim.solution["Discharge capacity [A.h]"].entries[-1])
        termination.append(sim.solution.termination)

    df = pd.DataFrame(
        data={
            "Cycle number": range(1, N + 1),
            "Discharge capacity [A.h]": capacity,
            "Termination": termination,
        }
    )

    return df