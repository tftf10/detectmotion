
#read a video file and detect change

#how 
#sample images at a set interval
#convert to greyscale + downscale
#determine a base background periodically, larger interval than the sampling, average over #many samples, rolling average.
#if deviation of sample greater than set tolerance create clip and alert
#thumbnail of image that set off the alert
#cool down of the alert?
#could use mipmaps when resolution known
#box filter algorithm
#how to get a change in shape rather than a overall change in brightness?
import cv2 as cv
import numpy as np
from collections import deque

cam = cv.VideoCapture("test.mp4")
fps = cam.get(cv.CAP_PROP_FPS)
last_frame = cam.get(cv.CAP_PROP_FRAME_COUNT)
sample_rate = 2	# wait in seconds between test samples
bg_update_rate = 1	# number test samples before updating background image
frame_jump = fps*sample_rate
n_bg_samples = 5

frame_pos = 0
n_samples = 0
bg_image = None
bg_images = []      # keep a stack of bg images to average, FIFO

flag_diff = 100     # pixel difference that will cause a flag
min_flags = 15      # min no. of flagged pixels to raise alert
n_detected = 0

while(frame_pos < last_frame):
    cam.set(cv.CAP_PROP_POS_FRAMES, frame_pos)
    ret, frame = cam.read()
    flags = 0
    if ret:
        frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        frame = cv.resize(frame, (20, 15), interpolation = cv.INTER_AREA)	# box sampled?
        if frame_pos !=0:
            diff = np.absolute(np.array(bg_image) - np.array(frame))    # there's a function for this in cv lib
            #ideally you'd look for a block of difference, dumb way to achieve is by extreme downscaling
            for i, row in enumerate(diff):
                for j, cell in enumerate(row):
                    if cell >= flag_diff:       # make a high contrast difference image for debug
                        diff[i][j] = 256
                        flags = flags + 1
                    else:
                        diff[i][j] = 0

    if flags >= min_flags:
        cv.imwrite('detected' + str(n_detected)+'.jpg', frame)
        n_detected = n_detected + 1

    if n_samples % bg_update_rate == 0 and flags == 0:
        if frame_pos == 0:
            bg_image = frame
            bg_images = deque([bg_image] * (n_bg_samples))
        else:
            bg_images.pop()
            bg_images.appendleft(frame)
            bg_image = np.mean(bg_images, axis=0)

    n_samples = n_samples+1
    frame_pos = frame_pos+frame_jump

cv.imwrite('averaged.jpg', bg_image)