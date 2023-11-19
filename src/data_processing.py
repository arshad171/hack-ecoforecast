from functools import reduce
import os
import pandas as pd

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
    """
    # assert all units are in "MAW"
    assert all(df["UnitName"] == "MAW")

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


def preprocess_data(df):
    # TODO: Generate new features, transform existing features, resampling, etc.

    return df_processed


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

    # df = load_data(input_path)
    # df_clean = clean_data(df)
    # df_processed = preprocess_data(df_clean)
    save_data(data_df, os.path.join(output_path, "data.csv"))


if __name__ == "__main__":
    args = parse_arguments()
    # main(args.input_path, args.output_path)
    main("data-raw", "data-processed")
