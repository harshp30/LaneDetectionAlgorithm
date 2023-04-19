# Lane Detection Algorithm

import cv2
import numpy as np


'''
This function is used to draw the physical lines as a mask over the video (series of images)
'''
def draw_the_lines(image, lines):

    # create the distinct image for the lines [0,255] - all 0 values means black image
    lines_image = np.zeros((image.shape[0], image.shape[1], 3), dtype=np.uint8)

    # there are (x,y) for the starting and end points for the lines
    for line in lines:
        for x1, y1, x2, y2 in line:
            cv2.line(lines_image, (x1, y1), (x2, y2), (0, 0, 255), thickness=5)

    # finally we have to merge the image with the lines
    image_with_lines = cv2.addWeighted(image, 0.8, lines_image, 1, 0.0)

    return image_with_lines


'''
This function is used to narrow down the sequence of images from the video into a triangular polygon
because that is the region within which lane lines appear and we can ignore the rest of the image
'''
def region_of_interest(image, region_points):
    # replace pixels with 0 (black) - the regions we are not interested
    mask = np.zeros_like(image)
    # the region that we are interested in is the lower triangle - 255 white pixels
    cv2.fillPoly(mask, region_points, 255)
    # use the mask: we want to keep the regions of the original image where
    # the mask has white colored pixels
    masked_image = cv2.bitwise_and(image, mask)
    return masked_image


'''
This function is used to fund the lane lines within the image by using various techniques
such as gray scaling, canny algorithm, and hough lines algorithm
'''
def get_detected_lanes(image):

    (height, width) = (image.shape[0], image.shape[1])

    # we have to turn the image into grayscale
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # edge detection kernel (Canny's Algorithm)
    canny_image = cv2.Canny(gray_image, 100, 120)

    # we are interested in the "lower region" of the image (there are the driving lanes)
    region_of_interest_vertices = [
        (0, height),  # bottom left of image
        (width*0.5, height*0.65),  # middle top of the image
        (width, height)  # bottom right of the image
    ]

    # get rid of the un-relevant part of the image only keep the lower trial region
    cropped_image = region_of_interest(canny_image, np.array([region_of_interest_vertices], np.int32))

    # use the line detection algorithm (radians instead of degrees 1 degree = pi / 180)
    lines = cv2.HoughLinesP(cropped_image, rho=2, theta=np.pi/180, threshold=50, lines=np.array([]),
                           minLineLength=40, maxLineGap=150)

    # draw the lines on the image
    image_with_lines = draw_the_lines(image, lines)

    return image_with_lines


# video is equal to several images (frames) shown in sequence
video = cv2.VideoCapture('video/lane_detection_video.mp4')

# Iterate through each frame in the video
while video.isOpened():

    is_grabbed, frame = video.read()

    # if end of the video has been reached
    if not is_grabbed:
        break

    frame = get_detected_lanes(frame)

    # Show window
    cv2.imshow('Lane Detection Video', frame)
    cv2.waitKey(100)

# Destroy all windows and close
video.release()
cv2.destroyAllWindows()
