from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array
import pickle
import os
import cv2
import numpy as np


class Classifier:
    def __init__(self, model_path, labels_path):
        print("[INFO] loading model")
        self.model = load_model(model_path)
        self.labels = pickle.loads(open(labels_path, "rb").read())
        self.prob = 0.0


    def classify(self, frame):
        # Resize frame for classification
        frame = cv2.resize(frame, (96, 96)) / 255.0
        frame = img_to_array(frame)

        # Classify the image
        probabilities = self.model.predict(frame)[0]
        index = np.argmax(probabilities)
        self.prob = probabilities[index]
        result = self.labels.classes_[index]

        return result
