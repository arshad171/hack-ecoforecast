import pandas as pd
import tensorflow as tf

from config import *


def create_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """
    creates timeseries data sequence for forecasting
    params:
        df: dataframe
    retunrs: tf.keras.preprocessing.sequence.TimeseriesGenerator
    """
    # pad (TIME_LENGTH - 1) with in the begining since we don't have an history for the first sample
    pad = [pd.DataFrame(df.iloc[0, :]).transpose() for _ in range(TIME_LENGTH - 1)]
    df_temp = pd.concat(
        [*pad, df, pd.DataFrame(df.iloc[-1, :]).transpose()],
        ignore_index=True,
    )

    dataset = tf.keras.preprocessing.sequence.TimeseriesGenerator(
        df_temp.to_numpy(),
        df_temp.to_numpy(),
        length=TIME_LENGTH,
        batch_size=BATCH_SIZE,
        stride=STRIDE,
    )

    return dataset
