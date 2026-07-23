import plotly.graph_objects as go
import numpy as np
from itertools import permutations

# The starting point
p = (3, 1, 2)

# Generate all 6 coordinate permutations (the mirrored points)
points = list(set(permutations(p)))
xs, ys, zs = zip(*points)

fig = go.Figure()

# Plot the 6 mirrored points
fig.add_trace(go.Scatter3d(
    x=xs, y=ys, z=zs,
    mode='markers+text',
    marker=dict(size=8, color='gold', line=dict(width=2, color='black')),
    text=[f"({x},{y},{z})" for x, y, z in points],
    textposition="top center",
    name="Mirrored Points"
))

# Helper function to generate the planes
u = np.linspace(0, 4, 10)
v = np.linspace(0, 4, 10)
U, V = np.meshgrid(u, v)

# Plane x = y
fig.add_trace(go.Surface(x=U, y=U, z=V, opacity=0.2, colorscale='Blues', showscale=False, name="Plane x=y"))
# Plane x = z
fig.add_trace(go.Surface(x=U, y=V, z=U, opacity=0.2, colorscale='Reds', showscale=False, name="Plane x=z"))
# Plane y = z
fig.add_trace(go.Surface(x=V, y=U, z=U, opacity=0.2, colorscale='Greens', showscale=False, name="Plane y=z"))

fig.update_layout(
    title="Interactive 3D Reflection Planes",
    scene=dict(
        xaxis_title='X Axis',
        yaxis_title='Y Axis',
        zaxis_title='Z Axis',
        xaxis=dict(range=[0, 4]),
        yaxis=dict(range=[0, 4]),
        zaxis=dict(range=[0, 4])
    ),
    margin=dict(l=0, r=0, b=0, t=40)
)

# This will automatically pop open a new tab in your web browser
fig.show()