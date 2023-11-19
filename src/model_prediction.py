import json
import os
import pandas as pd
import argparse

import tensorflow as tf

from data_utils import create_dataset
from constants import *


def load_data(file_path):
    """
    loads the training data.
    """
    df_test = pd.read_csv(
        os.path.join(file_path, "data-test.csv"), index_col="StartTime"
    )

    ds_test = create_dataset(df_test)

    return ds_test


def load_model(model_path):
    model = tf.keras.models.load_model(os.path.join(model_path, "model.keras"))
    return model


def make_predictions(model, ds) -> tf.Tensor:
    predictions = model.predict(ds)

    return predictions


def parse_predictions(predictions: tf.Tensor, input_file):
    metadata = json.load(fp=open(os.path.join(input_file, "transformations.json")))
    means = metadata["means"]
    stds = metadata["stds"]

    surplus = []
    for ix, region in enumerate(REGIONS):
        green_energy_pred = predictions[:, 2 * ix] * stds[2 * ix] + means[2 * ix]
        load_pred = predictions[:, 2 * ix + 1] * stds[2 * ix + 1] + means[2 * ix + 1]

        net = green_energy_pred - load_pred

        surplus.append(net)

    preds = tf.stack(surplus, axis=1)

    preds = tf.argmax(preds, axis=1).numpy().tolist()

    mapped_predictions = []

    for pred in preds:
        mapped_predictions.append(MAP_PREDICTIONS[REGIONS[pred]])

    return mapped_predictions


def save_predictions(predictions, predictions_file):
    predictions_to_save = {
        "target": {f"{ix}": pred for ix, pred in enumerate(predictions)}
    }

    json.dump(
        predictions_to_save,
        fp=open(os.path.join(predictions_file, "predictions.json"), "w"),
        indent=4,
    )


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Prediction script for Energy Forecasting Hackathon"
    )
    parser.add_argument(
        "--input_file",
        type=str,
        default="data/test_data.csv",
        help="Path to the test data file to make predictions",
    )
    parser.add_argument(
        "--model_file",
        type=str,
        default="models/model.pkl",
        help="Path to the trained model file",
    )
    parser.add_argument(
        "--output_file",
        type=str,
        default="predictions/predictions.json",
        help="Path to save the predictions",
    )
    return parser.parse_args()


def main(input_file, model_file, output_file):
    ds_test = load_data(input_file)
    model = load_model(model_file)
    predictions = make_predictions(model=model, ds=ds_test)
    final_predictions = parse_predictions(
        predictions=predictions, input_file=input_file
    )
    save_predictions(final_predictions, output_file)


if __name__ == "__main__":
    args = parse_arguments()
    # main(args.input_file, args.model_file, args.output_file)
    main("data-processed", "models", "predictions")
