import cv2
import numpy as np
from constants import THRESHOLD
import gbvision as gbv
from controller.tello import TelloVideoReceiver, TelloController

stdv = np.array([10, 100, 100])


def main():
    # start stream
    drone = TelloController()
    drone.start_stream()
    receive = TelloVideoReceiver()
    window = gbv.StreamWindow('feed', receive)
    while True:
        frame = window.show_and_get_frame()
        k = window.last_key_pressed
        if k == 'r':
            bbox = cv2.selectROI('feed', frame)
            thr = gbv.EMPTY_PIPELINE + THRESHOLD \
                  + gbv.Dilate(6) + gbv.Erode(2) + gbv.find_contours + gbv.contours_to_polygons + gbv.sort_polygons
            thr2 = gbv.EMPTY_PIPELINE + THRESHOLD + gbv.Dilate(6) + gbv.Erode(2)
            #thr =gbv.median_threshold(frame, stdv, bbox, gbv.ColorThreshold.THRESH_TYPE_HSV)
            break
    cv2.destroyAllWindows()

    threshold = gbv.StreamWindow('threshold', receive)
    threshold.open()
    threshold2 = gbv.StreamWindow('thr2', receive)
    threshold2.open()

    while True:
        status, frame = receive.read()
        list_contours = thr(frame)
        if not len(list_contours) == 0:
            list_contours = [list_contours[0]]
        drawn = gbv.draw_contours(np.zeros(frame.shape, np.uint8), list_contours, (255, 255, 255))
        if not window.show_frame(frame):
            break
        if not threshold.show_frame(drawn):
            break
        if not threshold2.show_frame(thr2(frame)):
            break

    window.close()
    threshold.close()
    drone.stop_stream()


if __name__ == '__main__':
    main()
