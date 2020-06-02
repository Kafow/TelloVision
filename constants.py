from gbvision import ColorThreshold
import os

THRESHOLD = ColorThreshold([[169, 189], [84, 255], [42, 242]], 'HSV')

MODEL_PATH = os.path.abspath('C:\\Users\\Ofek\\Desktop\\coding\\TelloVision')
LABELS_PATH = os.path.abspath('C:\\Users\\Ofek\\Desktop\\coding\\TelloVision\\label.pickle')
DATASET_PATH = os.path.abspath('dataset')

SPEED = 30
FPS = 120
