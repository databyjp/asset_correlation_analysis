# ========== (c) JP Hwang 16/3/21  ==========

import logging
import pandas as pd
import requests
import json
import random
import os
import utils

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

    # ========== Get symbols to use ==========
    # Get S&P 500 symbols
    sp_500_symbols = utils.get_sp_500_list()

    # Get n random symbols
    n_symbols = 30  # HOW MANY STOCKS SHOULD WE GET DATA FOR?
    symbol_list = random.sample(sp_500_symbols, n_symbols)

    # ========== Get symbols to use ==========
    with open("../../tokens/iex_token.txt", "r") as f:
        iex_tkn = f.read().strip()

    date_range = '3m'
    prices_list = list()
    for symbol in symbol_list:
        outpath = f"data/{symbol}_{date_range}.json"
        if not os.path.exists(outpath):  # Check that the file isn't already there
            resp = get_prices(symbol, iex_tkn, date_param=date_range)
            if resp is not None:
                prices_obj = parse_resp(resp)
                with open(outpath, "w") as f:
                    json.dump(prices_obj, f)
                prices_list.append(prices_obj)
        else:
            logger.info(f"Data exists for {outpath}, skipping")


if __name__ == '__main__':
    main()
