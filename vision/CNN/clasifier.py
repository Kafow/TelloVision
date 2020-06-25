from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array
import pickle
from collections import deque
import cv2
import numpy as np


class Classifier:
    def __init__(self, model_path, labels_path):
        print("[INFO] loading model")
        self.model = load_model(model_path)
        self.labels = pickle.loads(open(labels_path, "rb").read())
        self.prob = 0.0
        self.deque = deque(maxlen=50)

    def classify(self, frame):
        # Resize frame for classification
        frame = cv2.resize(frame, (64, 64)) / 255.0
        frame = img_to_array(frame)
        frame = np.expand_dims(frame, axis=0)

        # Classify the image
        probabilities = self.model.predict(frame)[0]
        self.deque.append(probabilities)
        result = np.array(self.deque).mean(axis=0)

        index = np.argmax(result)
        self.prob = probabilities[index]
        result = self.labels.classes_[index]

        return result
