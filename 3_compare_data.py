# ========== (c) JP Hwang 16/3/21  ==========

import logging
import pandas as pd
import numpy as np
import utils

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
    ticker_dict = utils.load_data("data")
    df = utils.ticker_dict_to_df(ticker_dict)
    df = utils.normalise_price(df)

    # ========== DETERMINE SIMILARITIES ==========
    # Calculate similarities between each stock


if __name__ == '__main__':
    main()
