# ========== (c) JP Hwang 16/3/21  ==========

import logging
import pandas as pd
import numpy as np
import utils
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

    corr_order = np.argsort(tmp_arr.flatten())
    corr_num = corr_order[-3]
    print(symbols[corr_num // len(symbols)], symbols[corr_num % len(symbols)])
    pos_pair_2 = [symbols[corr_num // len(symbols)], symbols[corr_num % len(symbols)]]

    for tmp_pair in [min_pair, neg_pair, pos_pair, pos_pair_2]:
        pair_df = df[df.symbol.isin(tmp_pair)]
        pair_piv_df = pair_df[["norm_close", "symbol", "date"]].pivot("date", "symbol")
        pair_piv_df = pair_piv_df.dropna()
        pair_piv_df.columns = pair_piv_df.columns.get_level_values(1)
        pair_piv_df = pair_piv_df.assign(avg=pair_piv_df.mean(axis=1)).reset_index()
        pair_df = pair_piv_df.melt(id_vars="date")
        fig = px.line(pair_df, x="date", y="value", color="symbol",
                      color_discrete_sequence=px.colors.qualitative.Safe,
                      title=f"Correlation - {utils.get_comp_name(tmp_pair[0])} & {utils.get_comp_name(tmp_pair[1])}",
                      height=400, width=800,
                      labels={"value": "Relative price", "date": "Date", "symbol": "Symbol"},
                      template="plotly_white")
        fig.show()
        fig.write_image(f"out_img/corr_{tmp_pair[0]}_{tmp_pair[1]}.png")


if __name__ == '__main__':
    main()
