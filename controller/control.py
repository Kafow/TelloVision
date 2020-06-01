from controller.tello import TelloVideoReceiver, TelloController
from vision.CNN.clasifier import Classifier
import pygame
import cv2
import numpy as np
import time
import threading
import abc
from constants import THRESHOLD, MODEL_PATH, LABELS_PATH, FPS, SPEED


class Controller(abc.ABC):
    def __init__(self):
        self.yaw_velocity = None
        self.for_back_velocity = None
        self.up_down_velocity = None
        self.tello = None
        self.in_control = None
        self.send_rc_control = None
        self.left_right_velocity = None

    @abc.abstractmethod
    def run(self):
        pass

    def update(self):
        if self.in_control:  # If in control
            if self.send_rc_control:
                self.tello.set_rc(self.left_right_velocity, self.for_back_velocity,
                                  self.up_down_velocity, self.yaw_velocity)


class ManualController(Controller):

    def __init__(self, tello: TelloController, stream: TelloVideoReceiver):
        super().__init__()
        pygame.init()
        pygame.display.set_caption("Tello video stream")
        self.screen = pygame.display.set_mode([960, 720])

        self.tello = tello
        self.video = stream
        self.in_control = True
        self.send_rc_control = False
        self.event = None

        self.for_back_velocity = 0
        self.left_right_velocity = 0
        self.up_down_velocity = 0
        self.yaw_velocity = 0

    def run(self):
        self.tello.stop_stream()
        self.tello.start_stream()

        if not self.video.isOpened():
            self.video.open(self.video.address)

        status, frame = self.video.read()

        should_stop = False
        while not should_stop and self.in_control:

            for event in pygame.event.get():
                self.event = event
                if event.type == pygame.USEREVENT + 1:
                    self.update()
                elif event.type == pygame.QUIT:
                    should_stop = True
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        should_stop = True
                    else:
                        self.keydown(event.key)
                elif event.type == pygame.KEYUP:
                    self.keyup(event.key)

            if not status:
                break

            self.screen.fill([0, 0, 0])

            status, frame = self.video.read()
            text = "Battery: {}%".format(self.tello.get_state()['bat'])
            cv2.putText(frame, text, (5, 720 - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = np.rot90(frame)
            frame = np.flipud(frame)

            background = pygame.surfarray.make_surface(frame)
            self.screen.blit(background, (0, 0))
            pygame.display.update()

            time.sleep(1 / FPS)
        if self.in_control:
            self.tello.land()
            self.tello.stop_stream()

    def keydown(self, key_event):
        if key_event == pygame.K_UP:  # set forward velocity
            self.for_back_velocity = SPEED
        elif key_event == pygame.K_DOWN:  # set backward velocity
            self.for_back_velocity = -SPEED
        elif key_event == pygame.K_LEFT:  # set left velocity
            self.left_right_velocity = -SPEED
        elif key_event == pygame.K_RIGHT:  # set right velocity
            self.left_right_velocity = SPEED
        elif key_event == pygame.K_w:  # set up velocity
            self.up_down_velocity = SPEED
        elif key_event == pygame.K_s:  # set down velocity
            self.up_down_velocity = -SPEED
        elif key_event == pygame.K_a:  # set yaw counter clockwise velocity
            self.yaw_velocity = -SPEED
        elif key_event == pygame.K_d:  # set yaw clockwise velocity
            self.yaw_velocity = SPEED

    def keyup(self, key_event):

        if key_event == pygame.K_UP or key_event == pygame.K_DOWN:  # set zero forward/backward velocity
            self.for_back_velocity = 0
        elif key_event == pygame.K_LEFT or key_event == pygame.K_RIGHT:  # set zero left/right velocity
            self.left_right_velocity = 0
        elif key_event == pygame.K_w or key_event == pygame.K_s:  # set zero up/down velocity
            self.up_down_velocity = 0
        elif key_event == pygame.K_a or key_event == pygame.K_d:  # set zero yaw velocity
            self.yaw_velocity = 0
        elif key_event == pygame.K_t:  # takeoff
            self.tello.takeoff()
            self.send_rc_control = True
        elif key_event == pygame.K_l:  # land
            not self.tello.land()
            self.send_rc_control = False


class VisionController(Controller):

    def __init__(self, tello: TelloController, video: TelloVideoReceiver):
        super().__init__()
        self.tello = tello
        self.video = video
        self.in_control = False

        self.yaw_velocity = None
        self.left_right_velocity = None
        self.for_back_velocity = None
        self.up_down_velocity = None

    def run(self):
        should_stop = False
        classifier = Classifier(MODEL_PATH, LABELS_PATH)
        direction = None
        engine = None  # To be in control of which direction we need to make speed 0
        while not should_stop and self.in_control:
            status, frame = self.video.read()
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = np.rot90(frame)
            frame = np.flipud(frame)
            frame = THRESHOLD(frame)

            if direction == 'up' or direction == 'down':
                engine = 'up_down'
            elif direction == 'left' or 'right':
                engine = 'left_right'

            direction = classifier.classify(frame)

            if direction == 'up':
                if engine == 'left_right':
                    self.left_right_velocity = 0
                self.up_down_velocity = SPEED

            elif direction == 'down':
                if engine == 'left_right':
                    self.left_right_velocity = 0
                self.up_down_velocity = -SPEED

            elif direction == 'left':
                if engine == 'up_down':
                    self.up_down_velocity = 0
                self.left_right_velocity = -SPEED

            elif direction == 'right':
                if engine == 'up_down':
                    self.up_down_velocity = 0
                self.left_right_velocity = SPEED

            if not status:
                break

        if self.in_control:
            self.tello.land()
            self.tello.stop_stream()

    def update(self):
        pass


class MainController:
    def __init__(self):
        self.tello = TelloController()
        self.video = TelloVideoReceiver()

        self.manual_controller = ManualController(self.tello, self.video)
        self.vision_controller = VisionController(self.tello, self.video)
        thread = threading.Thread(target=self.check_and_switch_controllers, daemon=True)
        thread.start()

    def check_and_switch_controllers(self):
        while True:
            key = cv2.waitKey(1) & 0xff
            if key == 0:
                self.tello.emergency()
            elif key == 20:
                self.manual_controller.in_control = not self.manual_controller.in_control
                self.vision_controller.in_control = not self.vision_controller.in_control

    def run(self):
        self.manual_controller.run()
        self.vision_controller.run()
