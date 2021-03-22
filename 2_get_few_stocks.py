# ========== (c) JP Hwang 16/3/21  ==========

import logging
import pandas as pd
import numpy as np
import requests
import json
import os
import utils
import plotly.express as px
import scipy.stats

logger = logging.getLogger(__name__)

desired_width = 320
pd.set_option('display.max_columns', 20)
pd.set_option('display.width', desired_width)


def parse_resp(resp):
    resp_obj = json.loads(resp.text)
    return resp_obj


def get_prices(symbol, key, date_param='5d'):

    url_prefix = "https://cloud.iexapis.com/stable/"

    path = f'stock/{symbol}/chart/{date_param}?chartCloseOnly=True&&token={key}'
    logger.info(f"Fetching {date_param} data for {symbol}")
    full_url = requests.compat.urljoin(url_prefix, path)

    try:
        resp = requests.get(full_url)
    except Exception as e:
        logger.exception(f"Exception {e} occurred!")
        return None

    if resp.status_code != 200:
        logger.error(f"Uh oh, something's wrong! Response code {resp.status_code} received.")
        return resp

    else:
        logger.info(f"Got the data")
        return resp


def main():
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    sh = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    sh.setFormatter(formatter)
    root_logger.addHandler(sh)

    # ========== Get token ==========
    with open("../../tokens/iex_token.txt", "r") as f:
        iex_tkn = f.read().strip()

    # ========== Get symbols to use ==========
    symbols = ["MSFT", "AAPL", "NVDA", "JNJ", "KHC", "ALL"]

    # ========== Get symbols to use ==========
    date_range = '3m'
    symbol_dict = dict()
    for symbol in symbols:
        outpath = f"data/{symbol}_{date_range}.json"
        if not os.path.exists(outpath):  # Check that the file isn't already there
            resp = get_prices(symbol, iex_tkn, date_param=date_range)
            if resp is not None:
                prices_obj = parse_resp(resp)
                with open(outpath, "w") as f:
                    json.dump(prices_obj, f)
                symbol_dict[symbol] = prices_obj
        else:
            logger.info(f"Data exists for {outpath}, skipping")
            with open(outpath, "r") as f:
                data_obj = json.load(f)
            symbol_dict[symbol] = data_obj

    df = utils.symbol_dict_to_df(symbol_dict)
    fig = px.line(df, x="date", y="close",
                  color="symbol", facet_col="symbol", facet_col_wrap=4,
                  category_orders={"symbol": list(np.sort(df["symbol"].unique()))},
                  width=1000, height=450,
                  template="plotly_white")
    fig.show()
    fig.write_image("out_img/msft_comp1.png")

    df = utils.normalise_price(df)
    fig = px.line(df, x="date", y="norm_close",
                  color="symbol", facet_col="symbol", facet_col_wrap=4,
                  category_orders={"symbol": list(np.sort(df["symbol"].unique()))},
                  width=1000, height=450,
                  template="plotly_white")
    fig.show()
    fig.write_image("out_img/msft_comp2.png")

    # ========== DETERMINE SIMILARITIES ==========
    # Calculate similarities between each stock
    r_array = np.zeros([len(symbols), len(symbols)])
    for i in range(len(symbols)):
        for j in range(len(symbols)):
            vals_i = df[df["symbol"] == symbols[i]]['norm_close'].values
            vals_j = df[df["symbol"] == symbols[j]]['norm_close'].values
            r_ij, _ = scipy.stats.pearsonr(vals_i, vals_j)
            r_array[i, j] = r_ij
            print(f"Correlation between {symbols[i]}, {symbols[j]}: {r_ij}")


if __name__ == '__main__':
    main()
