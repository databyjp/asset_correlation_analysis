# ========== (c) JP Hwang 16/3/21  ==========

import os
import json
import logging
import pandas as pd

logger = logging.getLogger(__name__)

desired_width = 320
pd.set_option('display.max_columns', 20)
pd.set_option('display.width', desired_width)


def load_data(data_dir="data"):
    json_list = [i for i in os.listdir(data_dir) if i.endswith(".json")]
    ticker_dict = dict()
    for json_file in json_list:
        ticker_name = json_file.split("_")[0]
        json_path = os.path.join(data_dir, json_file)
        try:
            with open(json_path, "r") as f:
                data_obj = json.load(f)
            ticker_dict[ticker_name] = data_obj
        except:
            logger.exception(f"Error loading {json_path}!")

    return ticker_dict


def ticker_dict_to_df(ticker_dict):
    tmp_df_list = list()
    for k, v in ticker_dict.items():
        tmp_df = pd.DataFrame(v)
        tmp_df = tmp_df.assign(ticker=k)
        tmp_df_list.append(tmp_df)
    df = pd.concat(tmp_df_list)
    return df


def normalise_price(df):
    df = df.assign(norm_close=0)
    for ticker in df["ticker"].unique():
        ticker_df = df[df["ticker"] == ticker]
        min_date = ticker_df["date"].min()
        ref_val = ticker_df[ticker_df["date"] == min_date]["close"].values[0]
        df.loc[df["ticker"] == ticker, "norm_close"] = df.loc[df["ticker"] == ticker, "close"] / ref_val
    return df


def main():
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    sh = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    sh.setFormatter(formatter)
    root_logger.addHandler(sh)


if __name__ == '__main__':
    main()
