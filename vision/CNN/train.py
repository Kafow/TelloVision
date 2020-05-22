from .model import CNN
from tensorflow.keras.optimizers import Adam
import matplotlib.pyplot as plt
from ..misc.images_to_dataset import ArrowsDataset

IMAGE_DIMS = (128, 128)

dataset = ArrowsDataset(args.path, IMAGE_DIMS)

(x_train, y_train), (x_test, y_test) = dataset.load_data()

model = CNN().build(IMAGE_DIMS[0], IMAGE_DIMS[1], 1, 4)

