#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 12 14:31:08 2021

Compute conduction times going left and going right through branch geometry

@author: tbury
"""

import numpy as np
import pandas as pd
import os

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import imageio.v2 as imageio

from funs import (
    mesh_single_branch_2,
    get_connections,
)

import json

names = sorted([n for n in os.listdir("output") if n[:4] == "2024"])[::-1]
name = names[0]

# Import config
with open(f"output/{name}/config.json", "r") as fp:
    config = json.load(fp)

# Import simulation data
filepath = f"output/{name}/df_voltage.csv"
df = pd.read_csv(filepath)


# ----------
# Get mapping from cell index to cell position
# ----------

# Create cell mesh that defines geometry
cell_mesh = mesh_single_branch_2(
    l1=config["l1"],
    w1=config["w1"],
    h=config["h"],
    # l2=config["l2"],
    w2=config["w2"],
    theta=config["theta"],
    # slope=config["slope"],
    # l_solo=config["l_solo"],
)

# Get connections
pos_to_index, connections = get_connections(cell_mesh)
index_to_pos = {value: key for key, value in pos_to_index.items()}


# ----------
# Compute conduction time
# ----------


def get_active_time(list_coords, thresh=0.5):
    """
    Compute first activation time of cells at cell_coords (averaged)
    """

    list_idx = [pos_to_index[coord] for coord in list_coords]
    list_cols = ["time"] + [f"cell {idx}" for idx in list_idx]
    df_left = df[list_cols]
    # Take mean over each cell at these positions
    series_v = df_left.set_index("time").mean(axis=1)
    # Find all active times
    active_times = series_v[series_v > thresh].index.values
    # If empty
    if len(active_times) == 0:
        return np.nan

    else:
        return active_times[0]


x1 = 20
x2 = 120
yvals = np.arange(config["h"], config["h"] + config["w1"])

# Left activation
list_coords = [(y, x1) for y in yvals]
active_time_left = get_active_time(list_coords)

# Right activation
list_coords = [(y, x2) for y in yvals]
active_time_right = get_active_time(list_coords)
