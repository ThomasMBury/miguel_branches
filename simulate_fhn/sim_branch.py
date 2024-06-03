#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2 June, 2024

Simulate the FK model on branch structure
Stimulate planar wave

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

from funs import mesh_single_branch, get_connections

import datetime
import pytz

import json


# Get date and time in zone ET
newYorkTz = pytz.timezone("America/New_York")
datetime_now = datetime.datetime.now(newYorkTz).strftime("%Y%m%d-%H%M%S")


### Define command line arguments
@dataclass
class Args:
    l1: int = 40
    """length of horizontal channel"""
    w1: int = 5
    """width of horizontal channel"""
    l2: int = 10
    """length of diagonal channel"""
    w2: int = 8
    """width of diagonal channel"""
    slope: int = 1
    """slope of diagonal channel"""
    l_solo: int = 5
    """length of section of horizontal channel before diag channel begins"""

    tmax: int = 200
    """time to run simulation up to"""
    log_interval: int = 2
    """how often to log system (number of time units)"""

    # FHN parameters
    fhn_eps: float = 0.015
    """relaxation speed of recovery variable"""
    fhn_a: float = 0.12
    """excitability of cell"""
    conductance: float = 1
    """Cell-to-cell conductance g, resulting in a current sum(g*(v_k-v)))"""

    # pacing params
    stim_right: bool = False
    """stimulate from the rhs or lhs"""
    stim_width: int = 2
    """width of area in which to stimulate"""


# Get CLI arguments
args = tyro.cli(Args)
args.ncells = args.l1 * args.w1 + args.l2 * args.w2
print(args)

# Export config data
dir_name = f"output/{datetime_now}/"
os.makedirs(dir_name, exist_ok=True)
json.dump(vars(args), open(dir_name + "config.json", "w"))

# ----------------
# Geometry
# ---------------

# Create cell mesh that defines geometry
cell_mesh = mesh_single_branch(
    l1=args.l1, w1=args.w1, l2=args.l2, w2=args.w2, slope=args.slope, l_solo=args.l_solo
)

# Get connections
pos_to_index, connections = get_connections(cell_mesh)
index_to_pos = {value: key for key, value in pos_to_index.items()}

# Define which cells to pace
list_coords_pace = []

# if stim on the left
if not args.stim_right:
    for y in range(args.w1):
        for x in range(args.stim_width):
            list_coords_pace.append((y, x))

# if stim on the right
else:
    for y in range(args.w1):
        for x in np.arange(args.l1 - args.stim_width, args.l1):
            list_coords_pace.append((y, x))

list_cells_pace = []
for coord in list_coords_pace:
    list_cells_pace.append(pos_to_index[coord])


# ----------------
# Cell model
# ----------------

# Load in model from mmt file
m = myokit.load_model("../mmt_files/fhn.mmt")

# Model parameters
eps = args.fhn_eps
a = args.fhn_a
b = 0.5
c = 1
d = 0

# Create pacing protocol (used for pre-pacing here)
bcl = 1000  # Pacing cycle length for cell
duration = 1  # Duration of impulse (ms)
level = 1  # Level of stimulus (1=full)
offset = 15

# Pre-pacing protocol for each cell
p_pre = myokit.pacing.blocktrain(bcl, duration, offset=offset, level=level)

# Pacing protocol for simulation
p = myokit.Protocol()
p.schedule(level, offset, duration)


# Dictionary of parameters to adjust in model
params = {}
params["membrane.epsilon"] = eps
params["membrane.a"] = a
params["membrane.b"] = b
params["membrane.c"] = c
params["membrane.d"] = d

# Simulation time step (sometimes need 2e-3 as opposed to default 5-e3 to get convergence)
dt = 5e-3

# Set parameters of model
for key in params.keys():
    try:
        m.set_value(key, params[key])
    except:
        "{} is not a valid parameter".format(key)

# Prepacing of single cell to set initial condition
s_cell = myokit.Simulation(m, p_pre)
num_beats_pre = 1000
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
    precision=64,
)


s.set_connections(connections)
# can check connections using s._connections

# Set simulation settings
s.set_state(state0)
s.set_step_size(step_size=dt)

# Time simulation
tic = time.perf_counter()

# Set up progress printer (-1 for update every 10%)
w = myokit.ProgressPrinter(digits=-1)

print("Run sim")
s.set_paced_cell_list(list_cells_pace)
log = s.run(
    args.tmax,
    log_interval=args.log_interval,
    log=["engine.time", "membrane.v"],
    progress=w,
)

# Save full data log as binary file
log.save(dir_name + "datalog", precision=64)

# Save data log as csv
log.save_csv(
    dir_name + "datalog.csv",
    precision=64,
    order=None,
    delimiter=",",
    header=True,
    meta=False,
)


# Datalog to pd.DataFrame
dic = {"time": np.array(log["engine.time"])}
for i in np.arange(0, args.ncells):
    dic["cell {}".format(i)] = log["{}.membrane.v".format(i)]
df = pd.DataFrame(dic)

filename = "df_voltage.csv"
df.to_csv(dir_name + filename, index=False)

s.reset()

toc = time.perf_counter()
# End of timer
print(f"Simulation took {toc - tic:0.4f} seconds")
