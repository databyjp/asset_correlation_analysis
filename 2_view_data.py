# ========== (c) JP Hwang 16/3/21  ==========

import logging
import pandas as pd
import numpy as np
import plotly.express as px
import utils

logger = logging.getLogger(__name__)

desired_width = 320
pd.set_option('display.max_columns', 20)
pd.set_option('display.width', desired_width)


def filter_n_symbols(df, n_symbols):
    tmp_symbols = np.sort(df["symbol"].unique())[:n_symbols]
    tmp_df = df[df["symbol"].isin(tmp_symbols)]
    return tmp_df


def main():
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    sh = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    sh.setFormatter(formatter)
    root_logger.addHandler(sh)

    # ========== GET DATA ==========
    symbol_dict = utils.load_data("data")
    df = utils.symbol_dict_to_df(symbol_dict)

    # ========== EXPLORE DATA ==========
    # Plot graph for the first 4 companies
    tmp_df = filter_n_symbols(df, 8)
    fig = px.line(tmp_df, x="date", y="close",
                  color="symbol", facet_col="symbol", facet_col_wrap=4,
                  category_orders={"symbol": list(np.sort(tmp_df["symbol"].unique()))},
                  template="plotly_white")
    fig.show()

    # Let's normalise the data and then show
    df = utils.normalise_price(df)
    tmp_df = filter_n_symbols(df, 8)
    fig = px.line(tmp_df, x="date", y="norm_close",
                  color="symbol", facet_col="symbol", facet_col_wrap=4,
                  category_orders={"symbol": list(np.sort(tmp_df["symbol"].unique()))},
                  template="plotly_white")
    fig.show()

    # Let's take a look at 24 rows
    tmp_df = filter_n_symbols(df, 24)
    fig = px.line(tmp_df, x="date", y="norm_close",
                  color="symbol", facet_col="symbol", facet_col_wrap=4,
                  category_orders={"symbol": list(np.sort(tmp_df["symbol"].unique()))},
                  template="plotly_white")
    fig.show()

    # How about all the rows?
    fig = px.line(df, x="date", y="norm_close",
                  color="symbol", facet_col="symbol", facet_col_wrap=8,
                  category_orders={"symbol": list(np.sort(df["symbol"].unique()))},
                  template="plotly_white")
    fig.show()
    # It begins to be very difficult to visually compare so many charts - let's try to do this numerically


if __name__ == '__main__':
    main()
