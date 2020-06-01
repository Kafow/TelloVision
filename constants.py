from gbvision import ColorThreshold
import os

THRESHOLD = ColorThreshold()

MODEL_PATH = os.path.abspath('model.h5')
LABELS_PATH = os.path.abspath('label.pickle')

SPEED = 30
FPS = 120
