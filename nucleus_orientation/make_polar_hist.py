import plotly.figure_factory as ff
import plotly.graph_objects as go

import numpy as np
import pandas as pd

df = pd.read_csv("data/DAPI_4_StarDist.csv", index_col=0)

ar_thresh = 1.1

theta_values = df[(df["Y"] > 470) & (df["AR"] > ar_thresh)]["FeretAngle"]

# Create bins for the histogram
bins = np.histogram(theta_values, bins=np.arange(0, 361, 20))  # 20 degree bins
bin_counts = bins[0]  # Frequency of data in each bin
bin_edges = bins[1]  # Bin edges (angular positions)

# Create a polar bar chart to simulate a histogram
fig = go.Figure(
    go.Barpolar(
        r=bin_counts,  # Radial counts (frequencies)
        theta=(bin_edges[:-1] + bin_edges[1:])
        / 2,  # Midpoint of each bin for angular position
        width=[20] * len(bin_counts),  # Bin width set to 20 degrees
        marker_color="blue",
        marker_line_color="black",
        marker_line_width=1,
        opacity=0.75,
    )
)

# Update layout for the polar chart
fig.update_layout(
    title="Polar Histogram on strand",
    polar=dict(
        radialaxis=dict(showticklabels=True, ticks="", range=[0, 45]),
        angularaxis=dict(
            tickmode="array", tickvals=np.arange(0, 360, 45)
        ),  # Set angular ticks
    ),
    showlegend=False,
)

# Show the plot
fig.write_html("figures/fig_polar_strand.html")


# -----------
# Branch
# -------------

theta_values = df[(df["Y"] < 470) & (df["AR"] > ar_thresh)]["FeretAngle"]

# Create bins for the histogram
bins = np.histogram(theta_values, bins=np.arange(0, 361, 20))  # 20 degree bins
bin_counts = bins[0]  # Frequency of data in each bin
bin_edges = bins[1]  # Bin edges (angular positions)

# Create a polar bar chart to simulate a histogram
fig = go.Figure(
    go.Barpolar(
        r=bin_counts,  # Radial counts (frequencies)
        theta=(bin_edges[:-1] + bin_edges[1:])
        / 2,  # Midpoint of each bin for angular position
        width=[20] * len(bin_counts),  # Bin width set to 20 degrees
        marker_color="blue",
        marker_line_color="black",
        marker_line_width=1,
        opacity=0.75,
    )
)

# Update layout for the polar chart
fig.update_layout(
    title="Polar Histogram on branch",
    polar=dict(
        radialaxis=dict(showticklabels=True, ticks="", range=[0, 45]),
        angularaxis=dict(
            tickmode="array", tickvals=np.arange(0, 360, 45)
        ),  # Set angular ticks
    ),
    showlegend=False,
)

# Show the plot
fig.write_html("figures/fig_polar_branch.html")
