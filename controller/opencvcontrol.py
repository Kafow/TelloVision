from pynput import keyboard
from controller.tello import TelloVideoReceiver, TelloController
from vision.CNN.clasifier import Classifier
import cv2
import numpy as np
import time
import threading
from constants import MODEL_PATH, LABELS_PATH, FPS, HORIZONTAL_SPEED, VERTICAL_SPEED
from vision.vision import process_image_gaussian


def set_interval(func, sec):
    def func_wrapper():
        set_interval(func, sec)
        func()
    t = threading.Timer(sec, func_wrapper)
    t.start()
    return t


class MainController:
    def __init__(self):
        self.tello = TelloController()
        self.video = TelloVideoReceiver()
        self.classifier = Classifier(MODEL_PATH, LABELS_PATH)

        self.is_vision_control = False
        self.should_stop = False
        self.send_rc_control = False

        self.for_back_velocity = 0
        self.left_right_velocity = 0
        self.up_down_velocity = 0
        self.yaw_velocity = 0

    def run(self):
        """
        Runs the program based on vision or manual control.
        always starting with manual control.
        Manual control keys:
                   w - up
         a - yaw left  s - down  d - yaw right
                   ⬆️ - forward
         ⬅️ - left  ⬇️ - back  ➡️ - right
         l - land
         enter - emergency
         escape - quit
         space - switch between vision and manual control

        Returns:

        """
        listener = keyboard.Listener(
            on_press=self.keydown,
            on_release=self.keyup
        )
        listener.start()

        self.tello.stop_stream()
        self.tello.start_stream()

        if not self.video.isOpened():
            open_video = self.video.open(self.video.address)
            time.sleep(5)
            if not open_video:
                return False

        status, frame = self.video.read()
        set_interval(self.update, ((1000 // FPS) / 1000))
        #################### Manual Control ####################
        while True:
            while not self.should_stop and not self.is_vision_control:
                if not status:
                    break
                status, frame = self.video.read()
                text = "Battery: {}%".format(self.tello.state['bat'])
                cv2.putText(frame, text, (5, 720 - 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

                cv2.imshow('Video', frame)
                cv2.waitKey(1)

            #################### Vision Control ####################
            classifier = self.classifier
            direction = None
            engine = None  # To be in control of which direction we need to make speed 0

            while not self.should_stop and self.is_vision_control:

                # Screen output and reading from stream
                status, frame = self.video.read()
                copy_frame = frame.copy()
                frame = process_image_gaussian(frame)

                text = "Battery: {}%".format(self.tello.state['bat'])
                cv2.putText(copy_frame, text, (5, 720 - 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                label = "{}: {:.2f}%".format(direction, classifier.prob * 100)
                cv2.putText(copy_frame, label, (10, 25), cv2.FONT_HERSHEY_SIMPLEX,
                            0.7, (0, 255, 0), 2)

                # handle the engines so we know what was last direction
                if direction == 'up' or direction == 'down':
                    engine = 'up_down'
                elif direction == 'left' or 'right':
                    engine = 'left_right'

                # Vision movement
                direction = classifier.classify(frame)
                # direction = classifier.classify(frame) if classifier.prob > 40.0 else 'random'

                if direction == 'up':
                    if engine == 'left_right':
                        self.left_right_velocity = 0
                    self.up_down_velocity = HORIZONTAL_SPEED
                    print("UP")

                elif direction == 'down':
                    if engine == 'left_right':
                        self.left_right_velocity = 0
                    self.up_down_velocity = -HORIZONTAL_SPEED
                    print("DOWN")

                elif direction == 'left':
                    if engine == 'up_down':
                        self.up_down_velocity = 0
                    self.left_right_velocity = -VERTICAL_SPEED
                    print("LEFT")

                elif direction == 'right':
                    if engine == 'up_down':
                        self.up_down_velocity = 0
                    self.left_right_velocity = VERTICAL_SPEED
                    print("RIGHT")

                elif direction == 'random':
                    self.left_right_velocity = 0
                    self.up_down_velocity = 0

                cv2.imshow('After vision', copy_frame)
                cv2.waitKey(1)

                if not status:
                    break
            if self.should_stop:
                break
        self.tello.land()
        self.tello.stop_stream()
        self.video.release()

    def update(self):
        if self.send_rc_control:
            self.tello.set_rc(self.left_right_velocity, self.for_back_velocity,
                              self.up_down_velocity, self.yaw_velocity)

    def keydown(self, key):
        if key == keyboard.Key.up:  # set forward velocity
            self.for_back_velocity = HORIZONTAL_SPEED
        elif key == keyboard.Key.down:  # set backward velocity
            self.for_back_velocity = -HORIZONTAL_SPEED
        elif key == keyboard.Key.left:  # set left velocity
            self.left_right_velocity = -VERTICAL_SPEED
        elif key == keyboard.Key.right:  # set right velocity
            self.left_right_velocity = VERTICAL_SPEED
        elif key == keyboard.KeyCode.from_char('w'):  # set up velocity
            self.up_down_velocity = HORIZONTAL_SPEED
        elif key == keyboard.KeyCode.from_char('s'):  # set down velocity
            self.up_down_velocity = -HORIZONTAL_SPEED
        elif key == keyboard.KeyCode.from_char('a'):  # set yaw counter clockwise velocity
            self.yaw_velocity = -HORIZONTAL_SPEED
        elif key == keyboard.KeyCode.from_char('d'):  # set yaw clockwise velocity
            self.yaw_velocity = HORIZONTAL_SPEED
        elif key == keyboard.Key.esc:
            self.should_stop = True
        elif key == keyboard.Key.enter:
            self.tello.emergency()
        elif key == keyboard.Key.space:
            self.is_vision_control = not self.is_vision_control  # Switch between vision and manual controller

    def keyup(self, key):
        if key == keyboard.Key.down or key == keyboard.Key.up:  # set zero forward/backward velocity
            self.for_back_velocity = 0
        elif key == keyboard.Key.right or key == keyboard.Key.left:  # set zero left/right velocity
            self.left_right_velocity = 0
        elif key == keyboard.KeyCode.from_char('w') or key == keyboard.KeyCode.from_char(
                's'):  # set zero up/down velocity
            self.up_down_velocity = 0
        elif key == keyboard.KeyCode.from_char('a') or key == keyboard.KeyCode.from_char('d'):  # set zero yaw velocity
            self.yaw_velocity = 0
        elif key == keyboard.KeyCode.from_char('t'):  # takeoff
            if not self.tello.takeoff():
                print("[ERROR] Takeoff failed")
            else:
                self.send_rc_control = True
        elif key == keyboard.KeyCode.from_char('l'):  # land
            self.tello.land()
            self.send_rc_control = False
