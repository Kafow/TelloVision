from gbvision import ColorThreshold
import os

THRESHOLD = ColorThreshold([[169, 189], [84, 255], [42, 242]], 'HSV')

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = ROOT_DIR
LABELS_PATH = os.path.join(ROOT_DIR, 'label.pickle')
DATASET_PATH = os.path.join(ROOT_DIR, 'dataset')

IMAGE_DIMS = (64, 64)
BATCH_SIZE = 32
LR = 1e-3
EPOCHS = 10
LOSS = "categorical_crossentropy"

HORIZONTAL_SPEED = 35
VERTICAL_SPEED = 28
FPS = 120
