from tensorflow.keras.optimizers import Adam
import matplotlib.pyplot as plt
import argparse
import pickle
from vision import CNN
from vision import ArrowsDataset

# Arguments parser
parser = argparse.ArgumentParser()
parser.add_argument("-d", "--dataset", help="Path for dataset")
parser.add_argument("-m", "--model", help="The path for saving the model")
parser.add_argument("-l", "--label", help="Path for saving the label binary")
args = parser.parse_args()

IMAGE_DIMS = (64, 64)
BATCH_SIZE = 32
LR = 1e-3
EPOCHS = 10
LOSS = "categorical_crossentropy"

# Load Dataset
dataset = ArrowsDataset(args.dataset, IMAGE_DIMS)
(x_train, y_train), (x_test, y_test) = dataset.load_data()

# Init Model and compile
model = CNN().build(BATCH_SIZE, IMAGE_DIMS[0], IMAGE_DIMS[1], 1, 4)
opt = Adam(learning_rate=LR)
model.compile(loss=LOSS, optimizer=opt, metrics=['accuracy'])


# Train the model
output = model.fit(x_train, y_train, validation_data=(x_test, y_test), batch_size=BATCH_SIZE, epochs=EPOCHS)

try:
    with open(args.label, "wb") as f:
        print("[INFO] Saving labels bin...")
        f.write(pickle.dumps(dataset.lb))
        f.close()
except Exception as e:
    print(f"[ERROR] Saving labels failed: {e}")
model.save(args.model)

# Plotting
plt.plot(output.history['accuracy'])
plt.plot(output.history['val_accuracy'])
plt.title('model accuracy')
plt.ylabel('accuracy')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper left')
plt.show()

plt.plot(output.history['loss'])
plt.plot(output.history['val_loss'])
plt.title('model loss')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper left')
plt.show()

