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
    sectors_list = list(sp500_df.Sector.unique())

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
    out_list = list()
    
    # Set 1: n stocks from just one sector
    n_symbols = 10
    n_sectors = 7
    sects = random.sample(sectors_list, n_sectors)
    for i in range(n_sectors):
        sect = sects[i]
        temp_syms = [s for s in list(sp500_df[sp500_df.Sector == sect].Symbol.values) if s in df.symbol.unique()]
        temp_syms = random.sample(temp_syms, n_symbols)
        pf1_df = df[df.symbol.isin(temp_syms)]
        pf1_avg = get_avg_prices(pf1_df)
        pf1_var = pf1_avg.var()
        out_list.append({"Portfolio": sect, "Variance": pf1_var,
                         "returns": pf1_avg[-1] - 1, "symbols": temp_syms, "diversified": False})
        print(f"Variance for portfolio in {sect} sector: {pf1_var:.3f}")
        
        # Now diversify the portfolio
        new_syms = list()
        for sym in temp_syms:
            sym_ind = symbols.index(sym)
            corr_row = r_array[sym_ind]
            # corr_ind = np.argmin(np.abs(corr_row))
            corr_ind = np.argmin(corr_row)
            corr_sym = symbols[corr_ind]
            new_syms.append(corr_sym)
        div_syms = temp_syms + new_syms
        pf1d_df = df[df.symbol.isin(div_syms)]
        pf1d_avg = get_avg_prices(pf1d_df)
        pf1d_var = pf1d_avg.var()
        out_list.append({"Portfolio": sect, "Variance": pf1d_var,
                         "returns": pf1d_avg[-1] - 1, "symbols": div_syms, "diversified": True})
        print(f"Variance for portfolio in {sect} sector w/ neg. corr: {pf1d_var:.3f}")

    # Set 2: N random stocks
    n_random_portfolios = 4
    for i in range(n_random_portfolios):
        temp_syms = random.sample(symbols, n_symbols)
        pf2_df = df[df.symbol.isin(temp_syms)]
        pf2_avg = get_avg_prices(pf2_df)
        pf2_var = pf2_avg.var()
        out_list.append({"Portfolio": f"{n_symbols} random stocks - set {i+1}", "Variance": pf2_var,
                         "returns": pf2_avg[-1] - 1, "symbols": temp_syms, "diversified": False})
        print(f"Variance for {n_symbols} random stocks: {pf2_var:.3f}")
        # Now diversify the portfolio
        new_syms = list()
        for sym in temp_syms:
            sym_ind = symbols.index(sym)
            corr_row = r_array[sym_ind]
            # corr_ind = np.argmin(np.abs(corr_row))
            corr_ind = np.argmin(corr_row)
            corr_sym = symbols[corr_ind]
            new_syms.append(corr_sym)
        div_syms = temp_syms + new_syms
        pf2d_df = df[df.symbol.isin(div_syms)]
        pf2d_avg = get_avg_prices(pf2d_df)
        pf2d_var = pf2d_avg.var()
        out_list.append({"Portfolio": f"{n_symbols} random stocks - set {i+1}", "Variance": pf2d_var,
                         "returns": pf2d_avg[-1] - 1, "symbols": temp_syms, "diversified": True})
        print(f"Variance for {n_symbols} random stocks w/ diversification: {pf2d_var:.3f}")

    out_df = pd.DataFrame(out_list)
    out_df = out_df.assign(rel_risk=out_df["Variance"] / out_df["returns"])

    fig = px.bar(out_df, x="Portfolio", y="Variance", color="diversified", barmode="group",
                 title="Comparison of variance in hypothetical portfolios",
                 color_discrete_sequence=["DarkGray", "CadetBlue"] * (n_sectors + 1) + ["IndianRed"],
                 width=1000, height=600,
                 template="plotly_white")
    fig.show()
    fig.write_image("out_img/portfolio_vars.png")

    fig = px.bar(out_df, x="Portfolio", y="rel_risk", color="diversified", barmode="group",
                 title="Comparison of relative risk in hypothetical portfolios",
                 color_discrete_sequence=["DarkGray", "CadetBlue"] * (n_sectors + 1) + ["IndianRed"],
                 width=1000, height=600,
                 template="plotly_white")
    fig.show()
    fig.write_image("out_img/portfolio_rel_risk.png")


if __name__ == '__main__':
    main()
