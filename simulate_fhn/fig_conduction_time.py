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

names = sorted([n for n in os.listdir("output") if n[:4] == "2024"])[-2:]

list_dict = []
for name in names:
    with open(f"output/{name}/config.json", "r") as fp:
        config = json.load(fp)
    with open(f"output/{name}/active_times.json", "r") as fp:
        active_times = json.load(fp)
    config.update(active_times)
    list_dict.append(config)

df = pd.DataFrame(list_dict)


def get_cond_time(row):
    if row["stim_right"]:
        return row["active_left"] - row["active_right"]
    else:
        return row["active_right"] - row["active_left"]


df["cond_time"] = df.apply(get_cond_time, axis=1)


fig = px.line(df, x="theta", y="cond_time")
