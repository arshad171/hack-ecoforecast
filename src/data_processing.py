from functools import reduce
import os
import pandas as pd
import json

import argparse

from constants import *


def load_data(file_path) -> pd.DataFrame:
    # TODO: Load data from CSV file

    df = pd.read_csv(filepath_or_buffer=file_path)
    return df


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    clean the data. resamples in 15 min intervals and aggregtes by 1 hr
    missing values are imputed by linear linterpolation
    returns: clean dataframe
    """
    # assert all units are in "MAW"
    assert all(df["UnitName"] == "MAW"), "inconsistent metrics"

    time = pd.to_datetime(df["StartTime"].str[:-1], utc=True)

    df.set_index(time, inplace=True)
    # drop irrelevant cols
    df.drop(
        columns=["StartTime", "EndTime", "AreaID", "UnitName", "PsrType"],
        errors="ignore",
        inplace=True,
    )
    df = df[~df.index.duplicated(keep="first")]

    # upsample
    df.resample("15T").interpolate(method="linear", directions="both", inplace=True)
    # aggregate
    df_clean = df.groupby(pd.Grouper(freq="H")).sum()

    df_clean.interpolate(method="linear", directions="both", inplace=True)

    return df_clean


def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    preprocesses the data. scaling
    returns: df, transformations (dict, which can be saved as json for later use)
    """

    means = df.mean(axis=0)
    stds = df.std(axis=0)

    df_processed = (df - means) / stds

    transformations = {
        "columns": df_processed.columns.tolist(),
        "means": means.to_numpy().tolist(),
        "stds": stds.to_numpy().tolist(),
    }

    return df_processed, transformations


def save_data(df: pd.DataFrame, output_file):
    # TODO: Save processed data to a CSV file
    df.to_csv(output_file)


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Data processing script for Energy Forecasting Hackathon"
    )
    parser.add_argument(
        "--input_path",
        type=str,
        default="data/raw_data.csv",
        help="Path to the raw data file to process",
    )
    parser.add_argument(
        "--output_path",
        type=str,
        default="data/processed_data.csv",
        help="Path to save the processed data",
    )
    return parser.parse_args()


def parse_name(row):
    """
    parses the file name. eg: gen_DE_B01.csv -> [energy, DE, B01, is_green]
    """
    [name, _] = row["name"].split(".")
    name_split = name.split("_")
    energy = name_split[0]
    country = name_split[1]
    source = None if name.startswith("load") else name_split[2]

    row["energy"] = energy
    row["country"] = country
    row["source"] = source
    row["is_green"] = source in GREEN_SOURCES

    return row


def main(input_path, output_path):
    files = os.listdir(path=input_path)
    # create a df of filenames, easier to work with (split by country, type, etc)
    files_df = pd.DataFrame(data={"name": files})

    files_df = files_df.apply(parse_name, axis=1)

    files_df = files_df.groupby("country")

    data_dfs = []
    # iterate all the regions
    for region in REGIONS:
        group = files_df.get_group(region)
        region_dfs = []
        # for each group (region), read and preprocess all the csv files
        for _, row in group.iterrows():
            df = load_data(file_path=os.path.join(input_path, row["name"]))
            df_clean = clean_data(df=df)
            if row["energy"] == "gen":
                df_clean.rename(
                    columns={"quantity": f"quantity_{row['source']}"}, inplace=True
                )

            region_dfs.append(df_clean)

        # all csv data for a particular region
        region_df = reduce(
            lambda left, right: pd.merge(
                left, right, left_index=True, right_index=True, how="outer"
            ),
            region_dfs,
        )

        # add all green energy cols
        cols_to_add = list(
            filter(lambda col: col.startswith("quantity"), region_df.columns)
        )

        region_df = pd.DataFrame(
            data={
                f"green_energy_{region}": region_df[cols_to_add].sum(axis=1),
                f"{region}_Load": region_df["Load"],
            },
            index=region_df.index,
        )

        region_df.interpolate(method="linear", direction="both", inplace=True)

        data_dfs.append(region_df)

    # merge all regions for final csv
    data_df = reduce(
        lambda left, right: pd.merge(
            left, right, left_index=True, right_index=True, how="outer"
        ),
        data_dfs,
    )

    data_df.interpolate(method="linear", directions="both", inplace=True)
    data_df, transformations = preprocess_data(data_df)

    # df = load_data(input_path)
    # df_clean = clean_data(df)

    # split: train, val, test
    split_test = int(0.2 * len(data_df))

    test_df = data_df.iloc[-split_test:, :]
    train_df = data_df.iloc[:-split_test, :]

    split_val = int(0.1 * len(train_df))
    val_df = train_df.iloc[-split_val:, :]
    train_df = train_df.iloc[:-split_val, :]

    assert len(data_df) == len(test_df) + len(train_df) + len(val_df), "data overlap!"

    # save all data
    save_data(data_df, os.path.join(output_path, "data-all.csv"))
    save_data(train_df, os.path.join(output_path, "data-train.csv"))
    save_data(val_df, os.path.join(output_path, "data-val.csv"))
    save_data(test_df, os.path.join(output_path, "data-test.csv"))

    # dump transformations
    json.dump(
        transformations,
        open(os.path.join(output_path, "transformations.json"), mode="w"),
        indent=4,
    )


if __name__ == "__main__":
    args = parse_arguments()
    main(args.input_path, args.output_path)
    # main("data-raw", "data-processed")
