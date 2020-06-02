import gbvision as gbv
import cv2
import numpy as np


def process_image(frame):
    grayscaled = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # th = cv2.adaptiveThreshold(grayscaled, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 205, 1)
    blur = cv2.GaussianBlur(grayscaled, (5, 5), 0)
    th = cv2.threshold(blur, 120, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    th = np.bitwise_not(th)
    pipe = gbv.EMPTY_PIPELINE + gbv.find_contours + gbv.contours_to_polygons + gbv.sort_polygons
    list_contours = pipe(th)
    if not len(list_contours) == 0:
        list_contours = [list_contours[0]]
    drawn = gbv.draw_contours(np.zeros(frame.shape, np.uint8), list_contours, (255, 255, 255))
    img = cv2.cvtColor(drawn, cv2.COLOR_BGR2GRAY)
    return img
