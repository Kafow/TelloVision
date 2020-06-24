from controller.tello import TelloController, TelloVideoReceiver
import time
import cv2
class camaraData:
    def __init__(self):
        self.tello = TelloController()
        self.tello.start_stream()
        self.capture = TelloVideoReceiver()
        time.sleep(5)

    def print_cam_info(self):
        #         capture_mode = self.capture.get(cv2.CAP_PROP_MODE)
        #         print("Capture mode:", capture_mode)
        #         codec = self.capture.get(cv2.CAP_PROP_FOURCC)
        #         print("4-character code of codec:", codec)
        fps = self.capture.get(cv2.CAP_PROP_FPS)
        print("Framerate = %0.2f FPS" % (fps))
        self.current_gain = self.capture.get(cv2.CAP_PROP_GAIN)
        print("Gain = %0.2f" % (self.current_gain))
        print("Aperture = ", self.capture.get(cv2.CAP_PROP_APERTURE))
        print("Auto Exposure = ", self.capture.get(cv2.CAP_PROP_AUTO_EXPOSURE))
        print("Exposure = ", self.capture.get(cv2.CAP_PROP_EXPOSURE))
        print("Brightness = ", self.capture.get(cv2.CAP_PROP_BRIGHTNESS))
        print("Buffer Size = ", self.capture.get(cv2.CAP_PROP_BUFFERSIZE))
        print("Gamma = ", self.capture.get(cv2.CAP_PROP_GAMMA))
        print("Hue = ", self.capture.get(cv2.CAP_PROP_HUE))
        print("ISO Speed = ", self.capture.get(cv2.CAP_PROP_ISO_SPEED))
        print("Saturation = ", self.capture.get(cv2.CAP_PROP_SATURATION))
        print("Sharpness = ", self.capture.get(cv2.CAP_PROP_SHARPNESS))
        print("White Balance Blue U = ", self.capture.get(cv2.CAP_PROP_WHITE_BALANCE_BLUE_U))
        print("White Balance Red V = ", self.capture.get(cv2.CAP_PROP_WHITE_BALANCE_RED_V))

camaraData().print_cam_info()
