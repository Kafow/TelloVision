from imutils.paths import list_images
import cv2
import os
import numpy as np
import random

from sklearn.preprocessing import LabelBinarizer
from tensorflow.keras.preprocessing.image import img_to_array
from sklearn.model_selection import train_test_split

"""
Im not sure if i wanna use it because after I programmed this I found out Keras has 
tf.keras.preprocessing.image_dataset_from_directory() function who do basically the same
"""


class ArrowsDataset:
    def __init__(self, path_to_dataset, img_dims):
        """

        Args:
            path_to_dataset: Path of dataset
            img_dims: Dimensions of image
        """
        self.path = path_to_dataset
        self.img_dims = img_dims
        self.data = None
        self.labels = None
        self.lb = None

    def load_data(self):
        """
        Returns: Tuple of data splitted to train and test
        """
        data = []
        labels = []

        print("Loading images...")
        images_paths = sorted(list(list_images(self.path)))
        random.seed(69)
        random.shuffle(images_paths)

        for imagePath in images_paths:
            img = cv2.imread(imagePath)
            img = cv2.resize(img, self.img_dims)
            img = img_to_array(img)
            data.append(img)

            label = imagePath.split(os.path.sep)[-2]  # get the label according to folder name
            labels.append(label)

        # Make the images range from 0 to 1
        data = np.array(data, dtype=float) / 255.0

        # This will make the labels in binary form, [up,down,left,right] => array([[0, 0, 0, 1],
        #                                                                          [1, 0, 0, 0],
        #                                                                          [0, 1, 0, 0],
        #                                                                          [0, 0, 1, 0]])
        lb = LabelBinarizer()
        labels = lb.fit_transform(labels)

        self.data = data
        self.labels = labels
        self.lb = lb

        x_train, x_test, y_train, y_test = train_test_split(data, labels, test_size=0.2, random_state=69)

        return (x_train, y_train), (x_test, y_test)


