# ========== (c) JP Hwang 16/3/21  ==========

import logging
import pandas as pd
import numpy as np
import utils
import random
import scipy.stats
import plotly.express as px

logger = logging.getLogger(__name__)

desired_width = 320
pd.set_option('display.max_columns', 20)
pd.set_option('display.width', desired_width)


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
    df = utils.normalise_price(df)
    symbols = list(np.sort(df["symbol"].unique()))

    # ========== DETERMINE SIMILARITIES ==========
    # Calculate similarities between each stock
    r_array = np.zeros([len(symbols), len(symbols)])
    p_array = np.zeros([len(symbols), len(symbols)])
    for i in range(len(symbols)):
        for j in range(len(symbols)):
            vals_i = df[df["symbol"] == symbols[i]]['close'].values
            vals_j = df[df["symbol"] == symbols[j]]['close'].values
            r_ij, p_ij = scipy.stats.pearsonr(vals_i, vals_j)
            r_array[i, j] = r_ij
            p_array[i, j] = p_ij

    # ========== FIND PAIR HIGHEST(+ and -) & SMALLEST CORRELATIONS ==========
    min_corr = np.min(np.abs(r_array))
    neg_corr = np.min(r_array)
    tmp_arr = r_array.copy()
    for i in range(len(tmp_arr)):
        tmp_arr[i, i] = 0
    pos_corr = np.max(tmp_arr)

    min_inds = np.where(abs(r_array) == min_corr)
    neg_inds = np.where(r_array == neg_corr)
    pos_inds = np.where(r_array == pos_corr)

    min_pair = [symbols[min_inds[0][0]], symbols[min_inds[0][1]]]
    neg_pair = [symbols[neg_inds[0][0]], symbols[neg_inds[0][1]]]
    pos_pair = [symbols[pos_inds[0][0]], symbols[pos_inds[0][1]]]

    neg_df = df[df.symbol.isin(neg_pair)]
    neg_piv_df = neg_df[["norm_close", "symbol", "date"]].pivot("date", "symbol")
    neg_piv_df = neg_piv_df.dropna()
    neg_piv_df.columns = neg_piv_df.columns.get_level_values(1)
    neg_piv_df = neg_piv_df.assign(avg=(neg_piv_df["CERN"] + neg_piv_df["WYNN"]) / 2).reset_index()
    new_neg_df = neg_piv_df.melt(id_vars="date")
    fig = px.line(new_neg_df, x="date", y="value", color="symbol",
                  color_discrete_sequence=px.colors.qualitative.Safe,
                  title=f"Advantages of negative correlation - {utils.get_comp_name(neg_pair[0])} & {utils.get_comp_name(neg_pair[1])}",
                  height=400, width=800,
                  labels={"value": "Relative price", "date": "Date", "symbol": "Symbol"},
                  template="plotly_white")
    fig.show()

    # ========== VIEW SAMPLE RESULTS ==========
    n_symbols = 3
    symbol_samples = random.sample(range(len(symbols)), n_symbols)
    symbol_samples = [symbols.index("MSFT"), symbols.index("JNJ"), symbols.index("MMM"), symbols.index("JPM")]
    # For those symbols - get n closest & furthest symbols
    for i in symbol_samples:
        tmp_sym = symbols[i]
        closest_i = np.argsort(r_array[i])[-4:-1][::-1]
        furthest_i = np.argsort(r_array[i])[:3]
        closest_syms = [symbols[j] for j in closest_i]
        furthest_syms = [symbols[j] for j in furthest_i]
        print(f"For {tmp_sym}: closest symbols: {closest_syms}")
        print(f"For {tmp_sym}: furthest symbols: {furthest_syms}")
        tmp_df = df[df["symbol"].isin([tmp_sym]+closest_syms+furthest_syms)]
        fig = px.line(tmp_df, x="date", y="norm_close", color="symbol",
                      title=f"Most correlated stocks to {tmp_sym}",
                      color_discrete_sequence=["red"] + ["LightSalmon"] * n_symbols + ["LightSteelBlue"] * n_symbols,
                      category_orders={"symbol": [tmp_sym] + closest_syms + furthest_syms},
                      template="plotly_white")
        fig.show()



if __name__ == '__main__':
    main()
