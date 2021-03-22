# ========== (c) JP Hwang 16/3/21  ==========

import logging
import pandas as pd
import requests
import json
import plotly.express as px

logger = logging.getLogger(__name__)

desired_width = 320
pd.set_option('display.max_columns', 20)
pd.set_option('display.width', desired_width)


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

    date_range = "3m"
    symbol = "MSFT"
    resp = get_prices(symbol, iex_tkn, date_param=date_range)
    if resp is not None:
        prices_obj = json.loads(resp.text)
    df = pd.DataFrame(prices_obj)

    fig = px.line(df, x="date", y="close", template="plotly_white",
                  title=f"Stock price history for {symbol}",
                  height=800, width=1600)
    fig.show()
    fig.write_image("out_img/msft_example.png")


if __name__ == '__main__':
    main()
