#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2 June, 2024

Simulate the FK model on branch structure
Stimulate planar wave
Use cell mesh 2

@author: tbury
"""

import numpy as np
import pandas as pd
import os

import myokit as myokit
import matplotlib.pyplot as plt
import time
import myokit as myokit

import tyro
from dataclasses import dataclass

from funs import (
    mesh_single_branch,
    mesh_single_branch_2,
    get_connections,
    mesh_double_branch,
    mesh_double_branch_2,
)

import datetime
import pytz

import json


# Get date and time in zone ET
newYorkTz = pytz.timezone("America/New_York")
datetime_now = datetime.datetime.now(newYorkTz).strftime("%Y%m%d-%H%M%S")


### Define command line arguments
@dataclass
class Args:
    run_name: str = "mac"
    """name of the run"""
    save_voltage_data: bool = True
    """whether to save the voltage data at each log interval"""
    log_interval: float = 5
    """how often to log system (number of time units)"""
    tmax: int = 1000
    """time to run simulation up to"""
    double_precision: bool = False
    """whether to run OpenCL with 64-bit precision (doulbe) or 32-bit (single)"""
    dt: float = 2e-3
    """integration time step. 2e-3 or 5e-3 - smaller dt more stable"""

    l1: int = 60
    """length of horizontal channel before and after junction """
    w1: int = 5
    """width of horizontal channel"""
    h: int = 20
    """height of the diagonal channel"""
    w2: int = 5
    """width of diagonal channel"""
    theta: int = 150
    """angle of diagonal channel"""
    scale_up: int = 1
    """parameter to scale up all length parameters of geometry"""

    # Ord parametes
    conductance: float = 1 / 4
    """Cell-to-cell conductance g, resulting in a current sum(g*(v_k-v)))"""

    # pacing params
    # stim_right: bool = False
    # """stimulate from the rhs or lhs"""
    stim_width: int = 4
    """width of area in which to stimulate"""

    # conduction time parameters
    x1: int = 20
    """left location of where to record activation time"""
    x2: int = 120
    """right location of where to record activation time"""
    active_thresh: float = 0
    """threshold in state variable to register as active"""


# Get CLI arguments
args = tyro.cli(Args)
args.open_cl_precision = 64 if args.double_precision else 32
print(args)

# Export config data
dir_name = f"output/{datetime_now}-{args.run_name}/"
os.makedirs(dir_name, exist_ok=True)
json.dump(vars(args), open(dir_name + "config.json", "w"))


# ----------------
# Geometry
# ---------------

# Create cell mesh that defines geometry
cell_mesh = mesh_single_branch_2(
    l1=args.l1 * args.scale_up,
    w1=args.w1 * args.scale_up,
    h=args.h * args.scale_up,
    w2=args.w2 * args.scale_up,
    theta=args.theta,
)

# Count the number of cells
args.ncells = int(cell_mesh.sum())

# Get connections
pos_to_index, connections = get_connections(cell_mesh, conductance=args.conductance)
index_to_pos = {value: key for key, value in pos_to_index.items()}

# Define which cells to pace
list_coords_pace = []

# Apply stim on the left
# if not args.stim_right:
for y in np.arange(
    args.h * args.scale_up, args.h * args.scale_up + args.w1 * args.scale_up
):
    for x in range(args.stim_width):
        list_coords_pace.append((y, x))

# # if stim on the right
# else:
#     for y in np.arange(args.h, args.h + args.w1):
#         for x in np.arange(cell_mesh.shape[1] - args.stim_width, cell_mesh.shape[1]):
#             list_coords_pace.append((y, x))

list_cells_pace = []
for coord in list_coords_pace:
    list_cells_pace.append(pos_to_index[coord])


# ----------------
# Cell model
# ----------------

# Load in model from mmt file
m = myokit.load_model("../mmt_files/ord-2011_1d.mmt")

# Ord parameters

# Dictionary to map to param labels used in Torord
dict_par_labels = {
    "ina": "ina.GNa",  # inward sodium current
    "ito": "ito.Gto",  # transient outward current
    "ical": "ical.PCa",  # L-type calcium current
    "ikr": "ikr.GKr",  # Rapid late potassium current
    "iks": "iks.GKs",  # Slow late potassium current
    "inaca": "inaca.Gncx",  # sodium calcium exchange current
    "tjca": "ical.tjca",  # relaxation time of L-type Ca current
}


# Get default parameter values used in Ord (required to apply multipliers)
params_default = {
    par: m.get(dict_par_labels[par]).value() for par in dict_par_labels.keys()
}

# Dictionary of parameters to adjust in model
params = {}

# Channel conductance multipliers
ina_mult = 1
ical_mult = 1
ikr_mult = 1
iks_mult = 1
tjca_mult = 1
ito_mult = 1
inaca_mult = 1


params[dict_par_labels["ina"]] = params_default["ina"] * ina_mult
params[dict_par_labels["ical"]] = params_default["ical"] * ical_mult
params[dict_par_labels["ikr"]] = params_default["ikr"] * ikr_mult
params[dict_par_labels["iks"]] = params_default["iks"] * iks_mult
params[dict_par_labels["inaca"]] = params_default["inaca"] * inaca_mult
params[dict_par_labels["ito"]] = params_default["ito"] * ito_mult
params[dict_par_labels["tjca"]] = params_default["tjca"] * tjca_mult


# Create pacing protocol (used for pre-pacing here)
bcl = 1000  # Pacing cycle length for cell
duration = 1  # Duration of impulse (ms)
level = 1  # Level of stimulus (1=full)
offset = 0

# Pre-pacing protocol for each cell
p_pre = myokit.pacing.blocktrain(bcl, duration, offset=offset, level=level)

# Pacing protocol for simulation
p = myokit.Protocol()
p.schedule(level, offset, duration)


# Simulation time step (sometimes need 2e-3 as opposed to default 5-e3 to get convergence)
dt = args.dt

# Set parameters of model
for key in params.keys():
    try:
        m.set_value(key, params[key])
    except:
        "{} is not a valid parameter".format(key)

# Prepacing of single cell to set initial condition
s_cell = myokit.Simulation(m, p_pre)
num_beats_pre = 100
print("Run pre-pacing of {} beats for single cell".format(num_beats_pre))
s_cell.pre(num_beats_pre * bcl)
print("Pre-pacing of single cell finished")

# Get current state of cell to use as IC for cable simulation
state0 = s_cell.default_state()

print("Make OpenCL simulation object")
s = myokit.SimulationOpenCL(
    m,
    p,
    ncells=args.ncells,
    diffusion=True,
    precision=args.open_cl_precision,  # precision 64 required for ord to be stable
)

s.set_connections(connections)
# can check connections using s._connections

# Set simulation settings
s.set_state(state0)
s.set_step_size(step_size=dt)

print("Set cells to pace")
s.set_paced_cell_list(list_cells_pace)

# Time simulation
tic = time.perf_counter()

# Set up progress printer (-1 for update every 10%)
w = myokit.ProgressPrinter(digits=-1)

print("Run sim")
log = s.run(
    args.tmax,
    log_interval=args.log_interval,
    log=["engine.time", "membrane.V"],
    progress=w,
)

# # Save full data log as binary file
# log.save(dir_name + "datalog", precision=64)

# # Save data log as csv
# log.save_csv(
#     dir_name + "datalog.csv",
#     precision=64,
#     order=None,
#     delimiter=",",
#     header=True,
#     meta=False,
# )

# Datalog to pd.DataFrame
dic = {"time": np.array(log["engine.time"])}
for i in np.arange(0, args.ncells):
    dic["cell {}".format(i)] = log["{}.membrane.V".format(i)]
df = pd.DataFrame(dic)

filename = "df_voltage.csv"
if args.save_voltage_data:
    df.to_csv(dir_name + filename, index=False)

# ----------
# Compute conduction time between x1 and x2
# ----------


def get_active_time(list_coords):
    """
    Compute first activation time of cells at cell_coords (averaged)
    """

    list_idx = [pos_to_index[coord] for coord in list_coords]
    list_cols = ["time"] + [f"cell {idx}" for idx in list_idx]
    df_left = df[list_cols]
    # Take mean over each cell at these positions
    series_v = df_left.set_index("time").mean(axis=1)
    # Find all active times
    active_times = series_v[series_v > args.active_thresh].index.values
    # If empty
    if len(active_times) == 0:
        return np.nan

    else:
        return active_times[0]


yvals = np.arange(
    args.h * args.scale_up, args.h * args.scale_up + args.w1 * args.scale_up
)

# Left activation
list_coords = [(y, args.x1) for y in yvals]
active_time_left = get_active_time(list_coords)

# Right activation
list_coords = [(y, args.x2) for y in yvals]
active_time_right = get_active_time(list_coords)

# Export activation times
dict_active_times = dict(
    active_left=str(round(active_time_left, 3)),
    active_right=str(round(active_time_right, 3)),
)
json.dump(dict_active_times, open(dir_name + "active_times.json", "w"))

# ---------
# reset simulation
# ---------

s.reset()

toc = time.perf_counter()
# End of timer
print(f"Simulation took {toc - tic:0.4f} seconds")
