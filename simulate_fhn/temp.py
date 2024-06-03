import numpy as np
import matplotlib.pyplot as plt

# Define the dimensions of the rectangular domain
width = 20
height = 20

# Create an array to represent the rectangular domain
domain = np.zeros((height, width))

# Create a meshgrid for the domain
x = np.arange(0, width)
y = np.arange(0, height)
X, Y = np.meshgrid(x, y)

# Define the center and radius of the circle
center = (10, 10)
radius = 5

# Create an array to represent the circle
circle = ((X - center[0]) ** 2 + (Y - center[1]) ** 2) <= radius**2

# Combine the rectangular domain and the circle
geometry = np.logical_or(domain, circle)

# Create some random data for the heatmap
data = np.random.rand(height, width)

# Apply the geometry mask to the data
data_on_geometry = np.where(geometry, data, np.nan)

# Plot the heatmap on the geometry
plt.imshow(data_on_geometry, cmap="hot", interpolation="nearest")

# Add a colorbar for reference
plt.colorbar()

plt.show()
