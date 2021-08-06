# ========== (c) JP Hwang 3/8/21  ==========

import pandas as pd
import numpy as np
import scipy.stats

desired_width = 320
pd.set_option('display.max_columns', 20)
pd.set_option('display.width', desired_width)

# ==========================
# For datasets 1-3
# ==========================
df = pd.read_csv("data-vid/example_dataset1.csv", index_col=0)
df.head()
df["variable"].unique()
import plotly.express as px
fig = px.line(df, x="Time", y="value", color="variable")
fig.show()
fig = px.line(df, x="Time", y="value", color="variable", facet_col="variable")
fig.show()
fig = px.line(df, x="Time", y="value", color="variable",
              title="Example Dataset 1", template="plotly_dark", width=800, height=600)
fig.show()

# Calculate pearson coefficients
# Option 1
df = df.pivot('Time', 'variable', 'value').reset_index()  # df.pivot(index, columns, values)
df.head()
print(scipy.stats.pearsonr(df["Variable A"], df["Variable B"]))

# Option 2
print(df[df["variable"] == "Variable A"]["value"])
print(scipy.stats.pearsonr(df[df["variable"] == "Variable A"]["value"], df[df["variable"] == "Variable B"]["value"]))

# ==========================
# For dataset 4
# ==========================
df = pd.read_csv("data-vid/example_dataset4.csv", index_col=0)
df.head()
df.sym.unique()
fig = px.line(df, x="date", y="close", color="sym",
              title=f"Example Dataset - {df.sym.unique()}", template="plotly_dark", width=800, height=600)
fig.show()
fig = px.line(df, x="date", y="norm_close", color="sym",
              title=f"Example Dataset - {df.sym.unique()}", template="plotly_dark", width=800, height=600)
fig.show()
print(scipy.stats.pearsonr(df[df["sym"] == "AAPL"]["close"], df[df["sym"] == "MMM"]["close"]))

# But how would we compare many, many pairs of stocks?
# For example - if we are potentially interested in the S&P 500, that's 500 stocks - which includes almost 125,000 pairs of stocks
# This is where automation comes in handy
import utils

# ========== GET DATA ==========
symbol_dict = utils.load_data("data")
df = utils.symbol_dict_to_df(symbol_dict)
df = utils.normalise_price(df)
symbols = list(np.sort(df["symbol"].unique()))

# ========== DETERMINE SIMILARITIES ==========
# Calculate similarities between each stock
import datetime
starttime = datetime.datetime.now()
r_array = np.zeros([len(symbols), len(symbols)])
p_array = np.zeros([len(symbols), len(symbols)])
for i in range(len(symbols)):
    for j in range(len(symbols)):
        vals_i = df[df["symbol"] == symbols[i]]['close'].values
        vals_j = df[df["symbol"] == symbols[j]]['close'].values
        r_ij, p_ij = scipy.stats.pearsonr(vals_i, vals_j)
        r_array[i, j] = r_ij
        p_array[i, j] = p_ij
elapsed = datetime.datetime.now()-starttime  # Takes about 2 minutes

fig = px.imshow(r_array)
fig.show()

fig = px.imshow(r_array, x=symbols, y=symbols,
                color_continuous_scale=px.colors.sequential.Blues)
fig.show()

r_df = pd.DataFrame(r_array, index=symbols, columns=symbols)
tmp_ser = r_df.loc["MSFT", :].sort_values(ascending=False)
tmp_df = df[(df["symbol"] == "MSFT") | (df["symbol"] == "BAX")]
fig = px.line(df, x="date", y="norm_close", color="symbol",
              title=f"Example Comparison", template="plotly_dark", width=800, height=600)
fig.show()

# ========== SELECT PORTFOLIO ==========
# Find negatively correlated stocks to some companies

# AAPL, MSFT
init_syms = ["AAPL", "MSFT"]
new_syms = list()
n_targets = 1
for sym in init_syms:
    tmp_df = r_df[sym]
    new_syms += tmp_df.sort_values()[:n_targets].index.to_list()
new_syms = list(set(new_syms))
list(new_syms)
port_syms = init_syms + new_syms
filt_df = df[df.symbol.isin(port_syms)]

fig = px.line(filt_df, x="date", y="norm_close", color="symbol",
              title=f"Example Comparison", template="plotly_dark", width=800, height=600)
fig.show()

# Find lowest-correlated stocks to some companies
init_syms = ["AAPL", "MSFT"]
new_syms = list()
n_targets = 1
for sym in init_syms:
    tmp_df = r_df[sym]
    tmp_df = tmp_df[tmp_df > 0]
    new_syms += tmp_df.sort_values()[:n_targets].index.to_list()
new_syms = list(set(new_syms))
list(new_syms)
port_syms = init_syms + new_syms
filt_df = df[df.symbol.isin(port_syms)]

fig = px.line(filt_df, x="date", y="norm_close", color="symbol",
              title=f"Example Comparison", template="plotly_dark", width=800, height=600)
fig.show()


filt_df["init_syms"] = True
filt_df.loc[filt_df["symbol"].isin(new_syms), "init_syms"] = False
fig = px.line(filt_df, x="date", y="norm_close", color="symbol", facet_col="init_syms",
              title=f"Example Comparison", template="plotly_dark", width=800, height=600)
fig.show()

avg_df = filt_df.groupby('date').mean()["norm_close"].reset_index()
avg_df["symbol"] = "avg"
filt_df = pd.concat([filt_df, avg_df])
fig = px.line(filt_df, x="date", y="norm_close", color="symbol",
              title=f"Example Comparison", template="plotly_dark", width=800, height=600)
fig.show()

color_map = {s: "grey" for s in port_syms}
color_map["avg"] = "red"
fig = px.line(filt_df, x="date", y="norm_close", color="symbol",
              color_discrete_map=color_map,
              title=f"Example Comparison", template="plotly_dark", width=800, height=600)
fig.show()







