#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 12 14:31:08 2021

Fig to to vizualize conduction time as a function of theta and w2

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

import json


# Import conduction data and config data

# names = sorted([n for n in os.listdir("output") if n[:4] == "2024"])[-91:]
names = sorted([n for n in os.listdir("output") if n[:4] == "2024"])

list_dict = []
for name in names:
    with open(f"output/{name}/config.json", "r") as fp:
        config = json.load(fp)
    with open(f"output/{name}/active_times.json", "r") as fp:
        active_times = json.load(fp)
    config.update(active_times)
    list_dict.append(config)

df = pd.DataFrame(list_dict)
df["active_left"] = df["active_left"].astype(float)
df["active_right"] = df["active_right"].astype(float)


def get_cond_time(row):
    # if row["stim_right"]:
    #     return row["active_left"] - row["active_right"]
    # else:
    #     return row["active_right"] - row["active_left"]
    return row["active_right"] - row["active_left"]


# def get_hemi_theta(row):
#     if row["stim_right"]:
#         return 180 - row["theta"]
#     else:
#         return row["theta"]


def get_w_ratio(row):
    return row["w2"] / row["w1"]


df["cond_time"] = df.apply(get_cond_time, axis=1)
df["w_ratio"] = df.apply(get_w_ratio, axis=1)

# df["theta_hemi"] = df.apply(get_hemi_theta, axis=1)

# df_plot = df[["theta_hemi", "cond_time", "w2"]].sort_values(["w2", "theta_hemi"])
df_plot = df[["theta", "cond_time", "w_ratio", "fhn_eps"]].sort_values(
    ["w_ratio", "theta"]
)

fig = px.line(
    df_plot,
    x="theta",
    y="cond_time",
    color="w_ratio",
    # facet_col="fhn_eps",
    markers=True,
)
fig.write_html("figures/temp.html")
