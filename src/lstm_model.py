import tensorflow as tf


class LSTMModel(tf.keras.Model):
    """
    An LSTM model. Uses a hybrid arch to model global information and country specific features
    """

    def __init__(self, input_dim: int, time_dim: int, num_classes: int) -> None:
        super(LSTMModel, self).__init__()

        self.input_dim = input_dim
        self.time_dim = time_dim
        self.num_classes = num_classes

        self.model = None

        self._create_model()

    def _create_model(self):
        """
        a util function to create a the model.
        the model has a common backbone (LSTM) to model global information and specific LSTM heads for each country
        """
        inputs = tf.keras.Input(shape=(self.time_dim, self.input_dim))

        common_feats = tf.keras.layers.LSTM(units=10, return_sequences=True)(inputs)

        outputs = []
        # add a specific branch for each class
        for ix in range(self.num_classes):
            # local feature indicies corresponding to the original features
            f_lx = ix * 2
            f_ux = (ix + 1) * 2

            ### arch 1
            # clf = tf.keras.Sequential(
            #     [
            #         tf.keras.layers.InputLayer(
            #             input_shape=(self.time_dim, self.input_dim)
            #         ),
            #         tf.keras.layers.Lambda(lambda x: x[:, :, f_lx:f_ux]),
            #         tf.keras.layers.LSTM(units=3),
            #         tf.keras.layers.Dense(units=5, activation="relu"),
            #         tf.keras.layers.Dense(units=2),
            #     ]
            # )
            # outputs.append(
            #     clf(
            #         inputs,
            #     )
            # )

            ### arch 2
            ## a lambda layer to slice features for the specific region/class
            f1 = tf.keras.layers.Lambda(lambda x: x[:, :, f_lx : f_ux])(inputs)
            ## concat common feats and local features
            f2 = tf.keras.layers.Concatenate(axis=2)([f1, common_feats])
            f3 = tf.keras.layers.LSTM(units=5)(f2)
            f4 = tf.keras.layers.Dense(units=10, activation="relu")(f3)
            f5 = tf.keras.layers.Dense(units=2)(f4)
            outputs.append(f5)

        output = tf.keras.layers.Concatenate(axis=1)(outputs)
        self.model = tf.keras.Model(inputs=inputs, outputs=output)

    def call(self, inputs):
        """call function, just return the model outputs"""
        return self.model(inputs)
