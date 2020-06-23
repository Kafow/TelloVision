import cv2
import argparse
import os
# from constants import THRESHOLD
from vision.vision import process_image_gaussian


def get_frames_out(video_path, output_path):
    cap = cv2.VideoCapture(video_path)
    i = 0
    while cap.isOpened():
        ret, frame = cap.read()
        # extract the frame and apply filter
        if ret is True:
            # Apply contours filter
            frame = process_image_gaussian(frame)

            cv2.imwrite(f"{output_path}\\{i}.jpg", frame)
        else:
            cap.release()
        i += 1


if __name__ == '__main__':
    directions = ['up', 'down', 'right', 'left', 'random']
    for direction in directions:
        get_frames_out(os.path.join(os.getcwd(), f'dataset\\{direction}.avi'), os.path.join(os.getcwd(), f'dataset\\{direction}'))
    # Argument parser
    parser = argparse.ArgumentParser()
    # parser.add_argument("file", help="The path for the file")
    # parser.add_argument("-o", "--output", type=str, help="The output directory for the dataset")
    # args = parser.parse_args()
    #
    # output_path = os.path.join(os.getcwd(), args.output)
    # file_path = os.path.join(os.getcwd(), args.file)
    # get_frames_out(file_path, output_path)
