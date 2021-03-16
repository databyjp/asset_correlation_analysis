# ========== (c) JP Hwang 16/3/21  ==========

import logging
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

desired_width = 320
pd.set_option('display.max_columns', 20)
pd.set_option('display.width', desired_width)


def price_line(date_from, date_to):
    """
    Plot prices from / to particular dates
    :param date_from:
    :param date_to:
    :return:
    """
    return fig


def main():
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    sh = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    sh.setFormatter(formatter)
    root_logger.addHandler(sh)


if __name__ == '__main__':
    main()
