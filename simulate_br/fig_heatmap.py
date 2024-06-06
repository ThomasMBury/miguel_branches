#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 12 14:31:08 2021

Fig to visualise BR on grid via sequential heatmaps

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
    mesh_single_branch,
    mesh_single_branch_2,
    get_connections,
    mesh_double_branch,
    mesh_double_branch_2,
)

import json

names = sorted([n for n in os.listdir("output") if n[:4] == "2024"])[::-1]
name = names[0]

# Import config
with open(f"output/{name}/config.json", "r") as fp:
    config = json.load(fp)

scale_down = 1

filepath_figs = f"figures/{name}/"
os.makedirs(filepath_figs, exist_ok=True)

# Import simulation data
filepath = f"output/{name}/df_voltage.csv"
df = pd.read_csv(filepath)

# print(df["time"].unique)

# ----------
# Get mapping from cell index to cell position
# ----------

# Create cell mesh that defines geometry
cell_mesh = mesh_single_branch_2(
    l1=config["l1"],
    w1=config["w1"],
    h=config["h"],
    w2=config["w2"],
    theta=config["theta"],
)

# Get connections
pos_to_index, connections = get_connections(cell_mesh)
index_to_pos = {value: key for key, value in pos_to_index.items()}

# -----
# Make gif of heatmap at given times
# --------

title = "FHN model on grid"
times = np.arange(0, config["tmax"], 4)
images = []
for i, time in enumerate(times):

    # Baseline image to show region with no cells
    ar_plot = cell_mesh - 100

    df_plot = df[df["time"] == time]

    # Assign values
    for col in df_plot.columns[1:]:
        cell_idx = int(col.split(" ")[-1])
        cell_pos = index_to_pos[cell_idx]
        ar_plot[cell_pos] = df_plot[col].values[0]

    # ar_plot = df_plot.drop("time", axis=1).values.reshape(
    #     ydim // scale_down, xdim // scale_down
    # )

    fig = plt.figure(figsize=(4, 2))
    plt.imshow(
        ar_plot,
        vmin=-120,
        vmax=20,
        # aspect=1,
    )
    # plt.tick_params(left=False, labelleft=False)
    # plt.subplots_adjust(
    #     top=1,
    #     bottom=0,
    #     right=0.95,
    #     left=0.1,
    # )
    plt.title(f"\nt = {time}ms")
    plt.colorbar()
    # Save under temp figs dir
    filename = filepath_figs + f"fig_{time:03}.png"
    plt.savefig(filename)
    plt.close()
    print(f"saved fig to {filename}")
    images.append(filename)

# Create GIF from the images
gif_filename = f"figures/{name}/heatmap.gif"

with imageio.get_writer(gif_filename, mode="I", fps=20) as writer:
    for filename in images:
        image = imageio.imread(filename)
        writer.append_data(image)

# Clean up image files
for filename in set(images):
    os.remove(filename)

# Export config data
json.dump(config, open(f"figures/{name}/config.json", "w"))
