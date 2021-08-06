# ========== (c) JP Hwang 3/8/21  ==========

import logging
import pandas as pd
import numpy as np
import random
import plotly.express as px
import math

logger = logging.getLogger(__name__)

desired_width = 320
pd.set_option('display.max_columns', 20)
pd.set_option('display.width', desired_width)

# ====================
# Example 1 - straight lines
# ====================
ts = list(range(100))
y1s = list()
y2s = list()

y1 = 1
y2 = 1.5
for t in ts:
    y1 = y1 + 0.05
    y1s.append(y1)
    y2 = y2 + 0.04
    y2s.append(y2)
df = pd.DataFrame({'Time': ts, 'Variable A': y1s, 'Variable B': y2s})
df = df.melt(id_vars=["Time"], value_vars=["Variable A", "Variable B"])
fig = px.line(df, x="Time", y="value", template="plotly_dark", color="variable",
              title=f"Example - Dataset 1",
              labels={"variable": "Variable", "value": "Value", "var_a": "Variable A", "var_b": "Variable B"},
              height=400, width=700)
fig.show()
df.to_csv("data-vid/example_dataset1.csv")

# ====================
# Example 2 - sine waves
# ====================
ts = list(range(101))
y1s = list()
y2s = list()
for t in ts:
    y1 = math.sin(math.pi/25 * t)
    y1s.append(y1)
    y2 = math.sin(math.pi/25 * t) * 0.6
    y2s.append(y2)
df = pd.DataFrame({'Time': ts, 'Variable A': y1s, 'Variable B': y2s})
df = df.melt(id_vars=["Time"], value_vars=["Variable A", "Variable B"])
fig = px.line(df, x="Time", y="value", template="plotly_dark", color="variable",
              title=f"Example - Dataset 2",
              labels={"variable": "Variable", "value": "Value", "var_a": "Variable A", "var_b": "Variable B"},
              height=400, width=700)
fig.show()
df.to_csv("data-vid/example_dataset2.csv")

# ====================
# Example 3 - sine waves w/ noise
# ====================
ts = list(range(101))
y1s = list()
y2s = list()
for t in ts:
    y1 = math.sin(math.pi/25 * t)
    y1s.append(y1)
    y2 = math.sin(math.pi/25 * t) + (random.random()-0.5) * 0.3
    y2s.append(y2)
df = pd.DataFrame({'Time': ts, 'Variable A': y1s, 'Variable B': y2s})
df = df.melt(id_vars=["Time"], value_vars=["Variable A", "Variable B"])
fig = px.line(df, x="Time", y="value", template="plotly_dark", color="variable",
              title=f"Example - Dataset 3",
              labels={"variable": "Variable", "value": "Value", "var_a": "Variable A", "var_b": "Variable B"},
              height=400, width=700)
fig.show()
df.to_csv("data-vid/example_dataset3.csv")

# ====================
# Example 4 - stock pairs
# ====================
symbols = ["AAPL", "MMM"]
tmp_dfs = list()
for sym in symbols:
    tmp_df = pd.read_json(f"data/{sym}_3m.json")
    tmp_df["sym"] = sym
    tmp_df["norm_close"] = tmp_df["close"] / tmp_df["close"].mean()
    tmp_dfs.append(tmp_df)
df = pd.concat(tmp_dfs)
fig = px.line(df, x="date", y="norm_close", template="plotly_dark", color="sym",
              title=f"Example - Dataset 4",
              labels={"sym": "Symbol", "close": "Normalised Price}"},
              height=400, width=700)
fig.show()
df.to_csv("data-vid/example_dataset4.csv")
