import plotly.figure_factory as ff
import plotly.graph_objects as go

import numpy as np
import pandas as pd


df = pd.read_csv("data/DAPI_4_StarDist.csv", index_col=0)

x = df["X"]
y = -df["Y"]
theta = df["FeretAngle"]
u = np.cos(theta)
v = -np.sin(theta)

# Create quiver figure
fig = ff.create_quiver(
    x,
    y,
    u,
    v,
    scale=10,
    arrow_scale=0.5,
    line_width=2,
)
fig.update_xaxes(range=[-20, 740])
fig.update_yaxes(range=[-550, 0])

fig.write_html("figures/fig_vector_field.html")


#### Scale arrows by aspect ratio scaled btw 0 and 1
arrow_size = (df["AR"] - df["AR"].min()) / (df["AR"].max() - df["AR"].min())
# arrow_size = 1 - (df["Circ."] - df["Circ."].min()) / (
#     df["Circ."].max() - df["Circ."].min()
# )


u = arrow_size * np.cos(theta)
v = -arrow_size * np.sin(theta)
# Create quiver figure
fig = ff.create_quiver(
    x,
    y,
    u,
    v,
    scale=15,
    arrow_scale=0.5,
    line_width=2,
)
fig.update_xaxes(range=[-20, 740])
fig.update_yaxes(range=[-550, 0])
fig.write_html("figures/fig_vector_field_scaled.html")
