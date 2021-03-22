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


def get_avg_prices(df):
    tmp_piv_df = df[["norm_close", "symbol", "date"]].pivot("date", "symbol")
    tmp_piv_df = tmp_piv_df.dropna()
    tmp_piv_df.columns = tmp_piv_df.columns.get_level_values(1)
    avg_ser = tmp_piv_df.mean(axis=1)
    return avg_ser


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

    sp500_df = utils.get_sp_500_data()

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

    # ========== CONSTRUCT PORTFOLIOS ==========
    val_list = list()

    # Portfolio 1: Just one sector
    for sect in (list(sp500_df.Sector.unique())):
        sect_syms = sp500_df[sp500_df.Sector == sect].Symbol.values
        pf1_df = df[df.symbol.isin(sect_syms)]
        pf1_avg = get_avg_prices(pf1_df)
        pf1_std = pf1_avg.std()
        val_list.append({"Portfolio": sect, "Std. dev": pf1_std, "returns": pf1_avg[-1]-1})
        print(f"St. dev for portfolio in {sect} sector: {pf1_std:.3f}")

    # Portfolio 2: 1 stock each from N random sectors
    sectors_list = sp500_df.Sector.unique()
    rand_symbols = list()
    n_symbols = 10
    for sect in sectors_list:
        sym_in_sect = list(sp500_df[sp500_df.Sector == sect].Symbol.values)
        sym = random.choice(df[df.symbol.isin(sym_in_sect)].symbol.values)
        rand_symbols.append(sym)
    rand_symbols = random.sample(rand_symbols, n_symbols)
    pf2_df = df[df.symbol.isin(rand_symbols)]
    pf2_avg = get_avg_prices(pf2_df)
    pf2_std = pf2_avg.std()
    val_list.append({"Portfolio": f"{n_symbols} random stocks", "Std. dev": pf2_std, "returns": pf2_avg[-1]-1})
    print(f"St. dev for {n_symbols} random stocks: {pf2_std:.3f}")

    # Portfolio 4: All data
    pf4_df = df.copy()
    pf4_avg = get_avg_prices(pf4_df)
    pf4_std = pf4_avg.std()
    val_list.append({"Portfolio": "250 random stocks", "Std. dev": pf4_std, "returns": pf4_avg[-1]-1})
    print(f"St. dev for 250 random stocks: {pf4_std:.3f}")

    # Portfolio 3: Portfolio 2 but with negatively correlated stocks
    neg_symbols = list()
    for sym in rand_symbols:
        sym_ind = symbols.index(sym)
        corr_row = r_array[sym_ind]
        neg_corr_ind = np.argmin(corr_row)
        neg_sym = symbols[neg_corr_ind]
        neg_symbols.append(neg_sym)
    pf3_df = df[df.symbol.isin(rand_symbols + neg_symbols)]
    pf3_avg = get_avg_prices(pf3_df)
    pf3_std = pf3_avg.std()
    val_list.append({"Portfolio": f"{n_symbols} random stocks w/ neg. corr", "Std. dev": pf3_std, "returns": pf3_avg[-1]-1})
    print(f"St. dev for {n_symbols} random stocks w/ neg. corr: {pf3_std:.3f}")

    # Portfolio 5: Portfolio 2 but with least correlated stocks
    min_symbols = list()
    for sym in rand_symbols:
        sym_ind = symbols.index(sym)
        corr_row = r_array[sym_ind]
        min_corr_ind = np.argmin(np.abs(corr_row))
        min_sym = symbols[min_corr_ind]
        min_symbols.append(min_sym)
    pf5_df = df[df.symbol.isin(rand_symbols + min_symbols)]
    pf5_avg = get_avg_prices(pf5_df)
    pf5_std = pf5_avg.std()
    val_list.append({"Portfolio": f"{n_symbols} random stocks w/ min. corr", "Std. dev": pf5_std, "returns": pf5_avg[-1]-1})
    print(f"St. dev for {n_symbols} random stocks w/ neg. corr: {pf5_std:.3f}")

    val_df = pd.DataFrame(val_list)
    fig = px.bar(val_df, x="Portfolio", y="Std. dev", color="Portfolio",
                 title="Comparison of variance in hypothetical portfolios",
                 color_discrete_sequence=["DarkGray"] * (n_symbols + 1) + ["CadetBlue", "IndianRed", "CornflowerBlue", "DodgerBlue"],
                 width=1000, height=600,
                 template="plotly_white")
    fig.show()
    fig.write_image("out_img/portfolio_stds.png")

    fig = px.bar(val_df, x="Portfolio", y="returns", color="Portfolio",
                 title="Comparison of return in hypothetical portfolios",
                 color_discrete_sequence=["DarkGray"] * (n_symbols + 1) + ["CadetBlue", "IndianRed", "CornflowerBlue", "DodgerBlue"],
                 width=1000, height=600,
                 template="plotly_white")
    fig.show()
    fig.write_image("out_img/portfolio_returns.png")

    # ========== REPEAT PROCESS FOR DIFFERENT RANDOM STOCKS ==========

    new_val_list = list()
    for i in range(10):
        rand_symbols = list()
        n_symbols = 10
        for sect in sectors_list:
            sym_in_sect = list(sp500_df[sp500_df.Sector == sect].Symbol.values)
            sym = random.choice(df[df.symbol.isin(sym_in_sect)].symbol.values)
            rand_symbols.append(sym)
        rand_symbols = random.sample(rand_symbols, n_symbols)
        tmp_df = df[df.symbol.isin(rand_symbols)]
        tmp_avg = get_avg_prices(tmp_df)
        tmp_std = tmp_avg.std()
        new_val_list.append({"Portfolio": f"{n_symbols} random stocks set: {i+1}", "Std. dev": tmp_std, "returns": tmp_avg[-1]-1})
        print(f"St. dev for {n_symbols} random stocks: {tmp_std:.3f}")

        min_symbols = list()
        for sym in rand_symbols:
            sym_ind = symbols.index(sym)
            corr_row = r_array[sym_ind]
            min_corr_ind = np.argmin(np.abs(corr_row))
            min_sym = symbols[min_corr_ind]
            min_symbols.append(min_sym)
        tmp_df = df[df.symbol.isin(rand_symbols + min_symbols)]
        tmp_avg = get_avg_prices(tmp_df)
        tmp_std = tmp_avg.std()
        new_val_list.append({"Portfolio": f"Set {i+1} w/ neg. corr", "Std. dev": tmp_std, "returns": tmp_avg[-1]-1})
        print(f"St. dev for {n_symbols} random stocks w/ neg. corr: {pf3_std:.3f}")

    new_val_df = pd.DataFrame(new_val_list)

    fig = px.scatter(new_val_df, x="Std. dev", y="returns", color="Portfolio",
                     color_discrete_sequence=["DarkGray", "CornflowerBlue"],
                 width=1000, height=600,
                 template="plotly_white")
    fig.show()

    fig = px.bar(new_val_df, x="Portfolio", y="Std. dev", color="Portfolio",
                 title="Comparison of variance in hypothetical portfolios",
                 color_discrete_sequence=["DarkGray", "CornflowerBlue"],
                 width=1000, height=600,
                 template="plotly_white")
    fig.show()
    # fig.write_image("out_img/portfolio_stds.png")

    fig = px.bar(new_val_df, x="Portfolio", y="returns", color="Portfolio",
                 title="Comparison of return in hypothetical portfolios",
                 color_discrete_sequence=["DarkGray", "CornflowerBlue"],
                 width=1000, height=600,
                 template="plotly_white")
    fig.show()
    # fig.write_image("out_img/portfolio_returns.png")


if __name__ == '__main__':
    main()
