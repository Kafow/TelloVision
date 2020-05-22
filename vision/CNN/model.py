from tensorflow.keras.layers import Dense, Conv2D, MaxPool2D, Flatten, Activation, Dropout
from tensorflow.keras.models import Sequential


class CNN:
    @staticmethod
    def build(width, height, depth, num_of_outputs):
        """
        Defines custom made CNN that aims to classify between 4 arrows (up, down, left, right)
        Args:
            width: Width of img
            height: Height of image
            depth: How many depth does the image have (1 for greyscale, 3 for RGB)
            num_of_outputs: how many outputs there is
        """
        input_shape = (width, height, depth)

        model = Sequential()

        # First set of layers (CONV => relu => MaxPool)
        model.add(Conv2D(32, (3, 3), input_shape=input_shape))
        model.add(Activation('relu'))
        model.add(MaxPool2D(pool_size=(2, 2)))
        model.add(Dropout(0.25))  # Dropout forth of the neurons

        # Second set of Layers ((CONV => RELU) *2 => MaxPool)
        model.add(Conv2D(64, (3, 3), input_shape=input_shape))
        model.add(Activation('relu'))
        model.add(MaxPool2D(pool_size=(3, 3)))
        model.add(Conv2D(128, (3, 3), input_shape=input_shape))
        model.add(Activation('relu'))
        model.add(MaxPool2D(pool_size=(3, 3)))
        model.add(Dropout(0.25))

        # Third set of Layers ((CONV => RELU) *2 => MaxPool)
        model.add(Conv2D(128, (3, 3), input_shape=input_shape))
        model.add(Activation('relu'))
        model.add(MaxPool2D(pool_size=(3, 3)))
        model.add(Conv2D(128, (3, 3), input_shape=input_shape))
        model.add(Activation('relu'))
        model.add(MaxPool2D(pool_size=(3, 3)))
        model.add(Dropout(0.25))

        # Flatten the model
        model.add(Flatten())
        model.add(Dense(1024))
        model.add(Activation("relu"))
        model.add(Dropout(0.5))

        # Final output and applying softmax filter
        model.add(Dense(num_of_outputs))
        model.add(Activation("softmax"))

        return model


image = getdataset()  # (300, w, h, 1)
image = image / 255.0

model.compile(loss='catagorical_crossentropy', optimizer=Adam(lr=0.1), metrics=['accuracy'])

model.fit(x_train, y_train, validation_data=(x_test, y_test))

model.evaluate(x_test.y_test)
