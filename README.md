# Single Particle Model with electrolyte and Side Reactions (SPMe+SR)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.6624984.svg)](https://doi.org/10.5281/zenodo.6624984)

Scripts to reproduce the results of the article

> F. Brosa Planella, W. D. Widanage, [Systematic derivation of a Single Particle Model with Electrolyte and Side Reactions (SPMe+SR) for degradation of lithium-ion batteries](https://arxiv.org/abs/2206.05078), _Submitted for publication (arXiv:2206.05078)_ (2022).

If you find the code useful please cite our paper, and also use the PyBaMM command
```python3
pybamm.print_citations()
```
at the end of your script to print all the references that have contributed to the code (model, parameters, solvers...).

If you find any bugs, please open an issue.

## How to use the code?
Note that in order to run the code, you need to have the requirements installed and the virtual environment activated (see below). To generate the figures, you will first need to run the simulations and the RPTs to calculate the capacities, otherwise the other scripts will not work:
1. Run `run_experiments.py` to simulate the experiment. You can change the C-rates and the number of cycles in the script. Note that this step can take a long time.
2. Run `run_RPT.py` to calculate the capacities. You can change the C-rates and the number of cycles in the script, but you must have run the experiment previously. Note that this step can take a long time.
3. Run `make_figures.py` to reproduce Figures 3-5 of the article and those in the SI.

The remaining files do not require the data so can be run straight away:
* `compare_mesh_sizes.py`: generates csv files with the system size of each model for various mesh sizes. Settings can be changed on the script.
* `plot_mesh_sizes.py`: generates Figure 2 of the article.
* `time_models.py`: times the models to reproduce the results in Table 4. Settings can be change on the script. Note that this step can take a long time, and that `scikits.odes` solvers are only supporten in Linux and MacOs.

The file `auxiliary_functions.py` is needed as it includes some auxiliary functions that are called from the main scripts.

## How to install?
These installation instructions assume you have Python installed (versions 3.7, 3.8 or 3.9) and that you have also installed the `virtualenv` package which can be done by running
```bash
pip install virtualenv
```

### Linux & MacOS
1. Create a virtual environment (this is strongly recommended to avoid clashes with the dependencies)
```bash
virtualenv env
```

2. Activate the virtual environment
```bash
source env/bin/activate
```
The virtual environment can later be deactivated (if needed) by running
```bash
deactivate
```

3. Install requirements
```bash
pip install -r requirements.txt
```

4. (Optional) Install `scikits.odes` following the instruction in [PyBaMM docs](https://pybamm.readthedocs.io/en/latest/install/GNU-linux.html#optional-scikits-odes-solver)

### Windows
1. Create a virtual environment (this is strongly recommended to avoid clashes with the dependencies)
```bash
python -m virtualenv env
```

2. Activate the virtual environment
```bash
env\Scripts\activate.bat
```
The virtual environment can later be deactivated (if needed) by running
```bash
deactivate
```

3. Install requirements
```bash
pip install -r requirements.txt
```

4. Note that `scikits.odes` is not supported in Windows, so some scripts might fail.