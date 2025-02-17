import os
import random
import numpy as np
import tensorflow as tf

gpus = tf.config.experimental.list_physical_devices("GPU")

for gpu in gpus:
    tf.config.experimental.set_memory_growth(gpu, True)

def train(path):
    IMAGE_DIM = 256

    dataset = tf.keras.utils.image_dataset_from_directory(path, batch_size=64, image_size=(IMAGE_DIM, IMAGE_DIM), color_mode="rgb")
    dataset = dataset.map(lambda x, y: (x / 255.0, y))
    dataset_size = len(dataset)
    train_size = int(0.7 * dataset_size)
    validate_size = int(0.2 * dataset_size)
    evaluate_size = dataset_size - (train_size + validate_size)
    train_set = dataset.take(train_size)
    validate_set = dataset.skip(train_size).take(validate_size)
    evaluate_set = dataset.skip(train_size + validate_size).take(evaluate_size)

    model = tf.keras.Sequential(
    [
        tf.keras.layers.Conv2D(32, (3, 3), activation="relu", padding="same", input_shape=(IMAGE_DIM, IMAGE_DIM, 3)),
        tf.keras.layers.MaxPooling2D((2, 2)),
        tf.keras.layers.Conv2D(64, (3, 3), activation="relu", padding="same"),
        tf.keras.layers.MaxPooling2D((2, 2)),
        tf.keras.layers.Conv2D(128, (3, 3), activation="relu", padding="same"),
        tf.keras.layers.MaxPooling2D((2, 2)),
        tf.keras.layers.Conv2D(256, (3, 3), activation="relu", padding="same"),
        tf.keras.layers.MaxPooling2D((2, 2)),
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(128, activation="relu"),
        tf.keras.layers.Dropout(0.5),
        tf.keras.layers.Dense(1, activation="sigmoid")
    ])
    
    model.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])
    model.fit(train_set, epochs=20, validation_data=validate_set)
    model.evaluate(evaluate_set)
    model.save("model/model.keras")

    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    lite_model = converter.convert()

    with open("model/model.tflite", "wb") as file:
        file.write(lite_model)

def main() -> None:
    train("dataset/train")

if __name__ == "__main__":
    main()