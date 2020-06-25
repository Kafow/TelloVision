import gbvision as gbv
import cv2
import numpy as np
from constants import THRESHOLD


@gbv.PipeLine
def contours_to_polygons(cnts):
    """
    performs approxPolyDP algorithm on a list of contours

    :param cnts: the list of contours
    :return: a list of polygons from the contours
    """
    arc_lengths = map(lambda cnt: 0.03 * cv2.arcLength(cnt, True), cnts)
    return list(map(lambda cnt: cv2.approxPolyDP(cnt, next(arc_lengths), True), cnts))


def process_image_gaussian(frame):
    grayscaled = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(grayscaled, (5, 5), 0)
    th = cv2.threshold(blur, 120, 255, cv2.THRESH_BINARY)[1]
    th = np.bitwise_not(th)
    pipe = gbv.EMPTY_PIPELINE + gbv.find_contours + contours_to_polygons + gbv.sort_polygons
    list_polygons = pipe(th)
    list_polygons_filtered = []
    if not len(list_polygons) == 0:
        list_polygons = list_polygons[:min(len(list_polygons), 4)]
        for poly in list_polygons:
            if check_arrow(poly):
                list_polygons_filtered = [poly]
                break
    drawn = gbv.draw_contours(np.zeros(frame.shape, np.uint8), list_polygons_filtered, (255, 255, 255),
                              thickness=cv2.FILLED)
    img = cv2.cvtColor(drawn, cv2.COLOR_BGR2GRAY)
    return img


def process_image_gaussian_adaptive(frame):
    grayscaled = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # blur = cv2.GaussianBlur(grayscaled, (5, 5), 0)
    th = cv2.adaptiveThreshold(grayscaled, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 205, 1)
    th = np.bitwise_not(th)
    pipe = gbv.EMPTY_PIPELINE + gbv.find_contours + contours_to_polygons + gbv.sort_polygons
    list_polygons = pipe(th)
    list_polygons_filtered = []
    if not len(list_polygons) == 0:
        list_polygons = list_polygons[:min(len(list_polygons), 4)]
        for poly in list_polygons:
            if check_arrow(poly):
                list_polygons_filtered = [poly]
                break
    drawn = gbv.draw_contours(np.zeros(frame.shape, np.uint8), list_polygons_filtered, (255, 255, 255),
                              thickness=cv2.FILLED)
    img = cv2.cvtColor(drawn, cv2.COLOR_BGR2GRAY)
    return img


def process_image_color(frame):
    th = THRESHOLD(frame)
    pipe = gbv.EMPTY_PIPELINE + gbv.find_contours + contours_to_polygons + gbv.sort_polygons
    list_polygons = pipe(th)
    list_polygons_filtered = []
    if not len(list_polygons) == 0:
        list_polygons = list_polygons[:min(len(list_polygons), 4)]
        for poly in list_polygons:
            if check_arrow(poly):
                list_polygons_filtered = [poly]
                break
    drawn = gbv.draw_contours(np.zeros(frame.shape, np.uint8), list_polygons_filtered, (255, 255, 255),
                              thickness=cv2.FILLED)
    img = cv2.cvtColor(drawn, cv2.COLOR_BGR2GRAY)
    return img


def check_arrow(polygon):
    return polygon.shape[0] == 7
