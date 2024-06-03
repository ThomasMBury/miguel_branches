#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 12 14:31:08 2021

Fig to visualise FHN on grid via sequential heatmaps

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

from funs import mesh_single_branch, get_connections


import json

name = "20240603-123037"

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
cell_mesh = mesh_single_branch(
    l1=config["l1"],
    w1=config["w1"],
    l2=config["l2"],
    w2=config["w2"],
    slope=config["slope"],
    l_solo=config["l_solo"],
)

# Get connections
pos_to_index, connections = get_connections(cell_mesh)
index_to_pos = {value: key for key, value in pos_to_index.items()}


# Setup image
ar_plot = cell_mesh * -1


# -----
# Make gif of heatmap at given times
# --------

title = "FHN model on grid"
times = np.arange(0, config["tmax"], 20)
images = []
for i, time in enumerate(times):
    df_plot = df[df["time"] == time]

    # Assign values
    for col in df_plot.columns[1:]:
        cell_idx = int(df_plot.columns[3].split(" ")[-1])
        cell_pos = index_to_pos[cell_idx]
        ar_plot[cell_pos] = df_plot[col].values[0]

    # ar_plot = df_plot.drop("time", axis=1).values.reshape(
    #     ydim // scale_down, xdim // scale_down
    # )

    fig = plt.figure(figsize=(4, 4))
    plt.imshow(
        ar_plot,
        # vmin=-0.2,
        # vmax=0.8,
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
    images.append(filename)

# # Create GIF from the images
# # gif_filename = f"../figures/{name}/fhn_annulus_cond_{conductance}_n_{ncells}_a_{fhn_a}_eps_{fhn_eps}_action_{action_idx}.gif"
# # gif_filename = f"../figures/{name}/fhn_annulus_cond_{conductance}_n_{ncells}_a_{fhn_a}_eps_{fhn_eps}_stimdist_{stim_dist}_stimdelay_{stim_delay}_stimheight_{stim_height}.gif"
# gif_filename = f"../figures/{name}/fhn_grid_cond_{conductance}_n_{ncells}_a_{fhn_a}_eps_{fhn_eps}_stimdist_{stim_dist}_stimwidth_{stim_width}_stimheight_{stim_height}_2.gif"

# # gif_filename = f"../figures/{name}/fhn_annulus_cond_{conductance}_n_{ncells}_stim1_{stim_big}_stim2_{stim_small}_stimdist_{stim_dist}_eps_{eps}.gif"
# # gif_filename = f"../figures/{name}/fhn_annulus_cond_{conductance}_n_{ncells}_stimwidth_{stim_width}_stimdist_{stim_dist}_stimdelay_{stim_delay}_eps_{eps}.gif"
# with imageio.get_writer(gif_filename, mode="I", fps=20) as writer:
#     for filename in images:
#         image = imageio.imread(filename)
#         writer.append_data(image)

# # Clean up image files
# for filename in set(images):
#     os.remove(filename)
