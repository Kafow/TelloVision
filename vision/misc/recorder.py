import gbvision as gbv
from constants import DATASET_PATH, FPS
from controller import TelloVideoReceiver,TelloController
import threading
import cv2
import os
import time


class Recorder:
    def __init__(self, video_path, fps, video_time):
        self.is_timer_over = False
        self.recorder = gbv.OpenCVRecorder(video_path, fps)
        self.video_time = video_time

    def change_timer_status(self):
        self.is_timer_over = not self.is_timer_over

    def run(self):
        tello = TelloController()
        tello.start_stream()
        video = TelloVideoReceiver()
        time.sleep(5)
        timer = threading.Timer(self.video_time, self.change_timer_status)
        while True:
            if video.isOpened():
                timer.start()
                break
        while True:
            result, frame = video.read()
            if result and not self.is_timer_over:
                cv2.imshow('title', frame)
                cv2.waitKey(1)
                self.recorder.record(frame)
            if self.is_timer_over:
                video.release()
                break


recorder = Recorder(os.path.join(DATASET_PATH, 'random.avi'), FPS, 15)
recorder.run()
