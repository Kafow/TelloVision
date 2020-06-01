from gbvision import ColorThreshold
import os

THRESHOLD = ColorThreshold([0,0,0,0])

MODEL_PATH = os.path.abspath('model.h5')
LABELS_PATH = os.path.abspath('label.pickle')
DATASET_PATH = os.path.abspath('dataset')
SPEED = 30
FPS = 120
