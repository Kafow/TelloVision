from controller.tello import TelloVideoReceiver, TelloController
from vision.CNN.clasifier import Classifier
import pygame
import cv2
import numpy as np
import time
import threading
import abc
from constants import MODEL_PATH, LABELS_PATH, FPS, SPEED
from vision.vision import process_image


class Controller(abc.ABC):
    @abc.abstractmethod
    def run(self):
        pass


class ManualController(Controller):

    def __init__(self, tello: TelloController, stream: TelloVideoReceiver, screen):
        super().__init__()
        pygame.init()
        pygame.display.set_caption("Tello video stream")
        self.screen = screen

        self.tello = tello
        self.video = stream
        self.in_control = True
        self.send_rc_control = False

        self.enter_pressed = False
        self.space_pressed = False

        self.for_back_velocity = 0
        self.left_right_velocity = 0
        self.up_down_velocity = 0
        self.yaw_velocity = 0

        pygame.time.set_timer(pygame.USEREVENT + 1, 1000 // FPS)  # Update Timer

    def run(self):
        self.tello.stop_stream()
        self.tello.start_stream()

        if not self.video.isOpened():
            if not self.video.open(self.video.address):
                return False

        status, frame = self.video.read()

        should_stop = False
        while not should_stop and self.in_control:

            for event in pygame.event.get():
                if event.type == pygame.USEREVENT + 1:
                    self.update()
                elif event.type == pygame.QUIT:
                    should_stop = True
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        should_stop = True
                    elif event.key == pygame.K_RETURN:
                        self.enter_pressed = True
                    elif event.key == pygame.K_SPACE:
                        self.space_pressed = True
                    else:
                        self.keydown(event.key)
                elif event.type == pygame.KEYUP:
                    self.keyup(event.key)

            if not status:
                break

            self.screen.fill([0, 0, 0])

            status, frame = self.video.read()
            text = "Battery: {}%".format(self.tello.state['bat'])
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
            self.video.release()

    def update(self):
        if self.in_control:  # If in control
            if self.send_rc_control:
                self.tello.set_rc(self.left_right_velocity, self.for_back_velocity,
                                  self.up_down_velocity, self.yaw_velocity)

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
            if not self.tello.takeoff():
                print("[ERROR] Takeoff failed")
            else:
                self.send_rc_control = True
        elif key_event == pygame.K_l:  # land
            not self.tello.land()
            self.send_rc_control = False


class VisionController(Controller):
    def __init__(self, tello: TelloController, video: TelloVideoReceiver, screen):
        super().__init__()
        self.tello = tello
        self.video = video
        self.in_control = False
        self.screen = screen

        self.enter_pressed = False
        self.space_pressed = False

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

            # Pygame events
            for event in pygame.event.get():
                if event.type == pygame.USEREVENT + 1:
                    self.update()
                elif event.type == pygame.QUIT:
                    should_stop = True
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        should_stop = True
                    elif event.key == pygame.K_RETURN:
                        self.enter_pressed = True
                    elif event.key == pygame.K_SPACE:
                        self.space_pressed = True

            self.screen.fill([0, 0, 0])

            # Screen output and reading from stream
            status, frame = self.video.read()
            text = "Battery: {}%".format(self.tello.get_state()['bat'])
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = np.rot90(frame)
            frame = np.flipud(frame)
            frame = process_image(frame)

            # handle the engines so we know what was last direction
            if direction == 'up' or direction == 'down':
                engine = 'up_down'
            elif direction == 'left' or 'right':
                engine = 'left_right'

            # Vision movement
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

            # Pygame screen
            background = pygame.surfarray.make_surface(frame)
            self.screen.blit(background, (0, 0))
            pygame.display.update()

            time.sleep(1 / FPS)

            if not status:
                break

        if self.in_control:
            self.tello.land()
            self.tello.stop_stream()

    def update(self):
        if self.in_control:  # If in control
            self.tello.set_rc(self.left_right_velocity, self.for_back_velocity,
                              self.up_down_velocity, self.yaw_velocity)


class MainController:
    def __init__(self):
        self.tello = TelloController()
        self.video = TelloVideoReceiver()

        self.screen = pygame.display.set_mode([960, 720])

        self.manual_controller = ManualController(self.tello, self.video, self.screen)
        self.vision_controller = VisionController(self.tello, self.video, self.screen)

        thread = threading.Thread(target=self.check_and_switch_controllers, daemon=True)
        thread.start()

    def check_and_switch_controllers(self):
        while True:
            if self.manual_controller.in_control:
                if self.manual_controller.space_pressed:
                    self.manual_controller.in_control = not self.manual_controller.in_control
                    self.vision_controller.in_control = not self.vision_controller.in_control
                elif self.manual_controller.enter_pressed:
                    self.tello.emergency()
            if self.vision_controller.in_control:
                if self.vision_controller.space_pressed:
                    self.manual_controller.in_control = not self.manual_controller.in_control
                    self.vision_controller.in_control = not self.vision_controller.in_control
                elif self.vision_controller.enter_pressed:
                    self.tello.emergency()

    def run(self):
        self.manual_controller.run()
        # self.vision_controller.run()
