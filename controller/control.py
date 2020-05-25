from controller.tello import TelloVideoReceiver, TelloController
from vision.CNN.clasifier import classify
import pygame
import cv2
import numpy as np
import time

SPEED = 30
FPS = 30


class ManualController:

    def __init__(self, tello: TelloController, stream: TelloVideoReceiver):
        pygame.init()
        pygame.display.set_caption("Tello video stream")
        self.screen = pygame.display.set_mode([960, 720])

        self.tello = tello
        self.video = stream
        self.in_control = False
        self.send_rc_control = False

        self.for_back_velocity = 0
        self.left_right_velocity = 0
        self.up_down_velocity = 0
        self.yaw_velocity = 0

    def run(self):
        self.tello.connect()

        # In case streaming is on. This happens when we quit this program without the escape key.
        self.tello.stop_stream()
        self.tello.start_stream()

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
                    else:
                        self.keydown(event.key)
                elif event.type == pygame.KEYUP:
                    self.keyup(event.key)

            if not status:
                break

            self.screen.fill([0, 0, 0])

            text = "Battery: {}%".format(self.tello.get_state()['battery'])
            cv2.putText(frame, text, (5, 720 - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = np.rot90(frame)
            frame = np.flipud(frame)

            frame = pygame.surfarray.make_surface(frame)
            self.screen.blit(frame, (0, 0))
            pygame.display.update()

            time.sleep(1 / FPS)
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

    def update(self):
        if self.in_control:  # If in control
            if self.send_rc_control:
                self.tello.set_rc(self.left_right_velocity, self.for_back_velocity,
                                  self.up_down_velocity, self.yaw_velocity)


class VisionController:
    def __init__(self, tello: TelloController, stream: TelloVideoReceiver):
        self.Tello = tello
        self.receiver = stream
        self.in_control = False

    def run(self):
        pass

    def update(self):
        pass
