from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array
import pickle
import os
import cv2
import numpy as np


def classify(frame, model_path, labels_path):
    print("[INFO] loading model")
    model = load_model(model_path)
    label = pickle.loads(open(labels_path, "rb").read())

    # Resize frame for classification
    frame = cv2.resize(frame, (96, 96)) / 255.0
    frame = img_to_array(frame)

    # Classify the image
    probabilities = model.predict(frame)[0]
    index = np.argmax(probabilities)
    result = label.classes_[index]
    return result

