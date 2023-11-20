import os
import pandas as pd
import argparse

import tensorflow as tf

from data_utils import *
from lstm_model import LSTMModel


def load_data(file_path):
    """
    loads the data.
    returns: time series data (train, val, test)
    """
    df_train = pd.read_csv(
        os.path.join(file_path, "data-train.csv"), index_col="StartTime"
    )
    df_val = pd.read_csv(os.path.join(file_path, "data-val.csv"), index_col="StartTime")

    ds_train = create_dataset(df_train)
    ds_val = create_dataset(df_val)

    return ds_train, ds_val


def split_data(df):
    # TODO: Split data into training and validation sets (the test set is already provided in data/test_data.csv)
    return X_train, X_val, y_train, y_val


def train_model(ds_train, ds_val):
    """
    train the model.
    params: datasets (train, val, test)
    returns:
        model: trained model
        history: training history
    """
    # TODO: Initialize your model and train it
    # model = tf.keras.Sequential(
    #     [
    #         tf.keras.layers.InputLayer(input_shape=(LENGTH, INPUT_SIZE)),
    #         tf.keras.layers.LSTM(units=20),
    #         tf.keras.layers.Dense(units=25, activation="relu"),
    #         tf.keras.layers.Dense(units=INPUT_SIZE),
    #     ]
    # )
    model = LSTMModel(input_dim=INPUT_SIZE, time_dim=TIME_LENGTH, num_classes=9)

    model.compile(
        loss="mae",
        optimizer="adam",
        metrics="mae",
    )

    history = model.fit(
        ds_train,
        batch_size=BATCH_SIZE,
        epochs=EPOCHS,
        validation_data=ds_val,
    )

    return model, history


def save_model(model, model_path):
    """
    saves the model to model_path/model.keras
    """
    model.save(os.path.join(model_path, "model.keras"))


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Model training script for Energy Forecasting Hackathon"
    )
    parser.add_argument(
        "--input_file",
        type=str,
        default="data/processed_data.csv",
        help="Path to the processed data file to train the model",
    )
    parser.add_argument(
        "--model_file",
        type=str,
        default="models/model.pkl",
        help="Path to save the trained model",
    )
    return parser.parse_args()


def main(input_file, model_file):
    ds_train, ds_val = load_data(input_file)
    # X_train, X_val, y_train, y_val = split_data(df)
    model, history = train_model(
        ds_train=ds_train,
        ds_val=ds_val,
    )
    save_model(model, model_file)


if __name__ == "__main__":
    args = parse_arguments()
    main(args.input_file, args.model_file)
    # main("data-processed", "models")
