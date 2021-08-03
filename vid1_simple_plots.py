# ========== (c) JP Hwang 3/8/21  ==========

import logging
import pandas as pd
import numpy as np
import plotly.express as px

logger = logging.getLogger(__name__)
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
sh = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
sh.setFormatter(formatter)
root_logger.addHandler(sh)

desired_width = 320
pd.set_option('display.max_columns', 20)
pd.set_option('display.width', desired_width)

df = pd.read_csv("data-vid/player_data.csv")
df = df[df["height"].notna()]
df["ht_inches"] = df["height"].str.split("-").str[0].apply(lambda x: int(x) * 12) + df["height"].str.split("-").str[1].apply(lambda x: int(x))

fig = px.scatter(df, x="weight", y="ht_inches", template="plotly_dark",
              title=f"Height vs Weight",
              height=600, width=700,
              labels={'weight': "Weight (lbs)", "ht_inches": "Height (inches)"})
fig.show()

cal_rate = 600
x = list(range(120))
y = [cal_rate / 60 * i for i in x]
df = pd.DataFrame({'Minutes': x, 'Calories': y})
fig = px.scatter(df, x="Minutes", y="Calories", template="plotly_dark",
                 title=f"Calories burnt vs running time",
                 height=600, width=700)
fig.show()

df = pd.read_csv("data-vid/auto-mpg.csv")
fig = px.scatter(df, x="mpg", y="weight", template="plotly_dark",
              title=f"Car Fuel Efficiency vs Weight",
              height=600, width=700,
              labels={'weight': "Weight (lbs)", "mpg": "Fuel Efficiency (miles per gallon)"})
fig.show()

# Random walk data:
import random
ts = list(range(100))
y1s = list()
y2s = list()

y1 = 5
y2 = 5.5
for t in ts:
    tmp = random.random() - 0.5  # Correlated variable
    y1 = y1 + tmp
    y1s.append(y1)
    noise = (random.random() - 0.5) * 0.1
    y2 = y2 + (tmp * random.random() + noise)
    y2s.append(y2)
df = pd.DataFrame({'Time': ts, 'Variable A': y1s, 'Variable B': y2s})
df = df.melt(id_vars=["Time"], value_vars=["Variable A", "Variable B"])
fig = px.line(df, x="Time", y="value", template="plotly_dark", color="variable",
              title=f"Example - Positive correlation",
              labels={"variable": "Variable", "value": "Value", "var_a": "Variable A", "var_b": "Variable B"},
              height=600, width=700)
fig.show()


# Random walk - negative correlation:
import random
ts = list(range(100))
y1s = list()
y2s = list()
y1 = 5
y2 = 5.5
for t in ts:
    tmp = random.random() - 0.5  # Correlated variable
    y1 = y1 + tmp
    y1s.append(y1)
    noise = (random.random() - 0.5) * 0.1
    y2 = y2 + (tmp * (random.random() - 1) + noise)
    y2s.append(y2)
df = pd.DataFrame({'Time': ts, 'Variable A': y1s, 'Variable B': y2s})
df = df.melt(id_vars=["Time"], value_vars=["Variable A", "Variable B"])
fig = px.line(df, x="Time", y="value", template="plotly_dark", color="variable",
              title=f"Example - Negative correlation",
              labels={"variable": "Variable", "value": "Value", "var_a": "Variable A", "var_b": "Variable B"},
              height=600, width=700)
fig.show()

df = pd.DataFrame({'Time': ts, 'Variable A': y1s, 'Variable B': y2s})
df["Average"] = (df["Variable A"] + df["Variable B"]) / 2
df = df.melt(id_vars=["Time"], value_vars=["Variable A", "Variable B", "Average"])
fig = px.line(df, x="Time", y="value", template="plotly_dark", color="variable",
              title=f"Example - Negative correlation",
              labels={"variable": "Variable", "value": "Value", "var_a": "Variable A", "var_b": "Variable B"},
              height=600, width=700)
fig.show()

# ====================
# Other sample graphs
# ====================
ts = list(range(100))
y1s = list()
y2s = list()

y1 = 5
y2 = 5.5
for t in ts:
    tmp = random.random() - 0.5  # Correlated variable
    y1 = y1 + tmp
    y1s.append(y1)
    noise = (random.random() - 0.5) * 0.1
    y2 = y2 + (tmp * random.random() + noise)
    y2s.append(y2)
df = pd.DataFrame({'Time': ts, 'Variable A': y1s, 'Variable B': y2s})
df = df.melt(id_vars=["Time"], value_vars=["Variable A", "Variable B"])
fig = px.line(df, x="Time", y="value", template="plotly_dark", color="variable",
              title=f"Example - Dataset 1",
              labels={"variable": "Variable", "value": "Value", "var_a": "Variable A", "var_b": "Variable B"},
              height=400, width=700)
fig.show()

df_a = pd.read_json("data/AAPL_3m.json")
df_a["sym"] = "AAPL"
df_m = pd.read_json("data/MMM_3m.json")
df_m["sym"] = "MMM"
df = pd.concat([df_a, df_m])
fig = px.line(df, x="date", y="close", template="plotly_dark", color="sym",
              title=f"Example - Dataset 2",
              labels={"sym": "Symbol", "close": "Close"},
              height=400, width=700)
fig.show()
