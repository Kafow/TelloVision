from tensorflow.keras.models import load_model
from controller.tello import TelloVideoReceiver, TelloController
import time
import imutils
import cv2
from vision.vision import process_image
from vision.CNN.clasifier import Classifier
from constants import MODEL_PATH, LABELS_PATH

# tello = TelloController()
# tello.start_stream()
# receiver = TelloVideoReceiver()
receiver = cv2.VideoCapture(0)
time.sleep(5)
classifier = Classifier(MODEL_PATH, LABELS_PATH)

while True:
    status, frame = receiver.read()
    copy_frame = process_image(frame)
    label = classifier.classify(copy_frame)

    # build the label and draw the label on the image
    label = "{}: {:.2f}%".format(label, classifier.prob * 100)
    frame = imutils.resize(frame, width=400)
    cv2.putText(frame, label, (10, 25), cv2.FONT_HERSHEY_SIMPLEX,
                0.7, (0, 255, 0), 2)
    cv2.imshow("Output", frame)
    cv2.waitKey(1)
