# USAGE
# program to read a reference frame and check if the threshold value of the animal is correct for given conditions 

import numpy as np
import cv2
import glob, os, sys, time, datetime


BGR_COLOR = {'red': (0,0,255),
        'green': (127,255,0),
        'blue': (255,127,0),
        'yellow': (0,127,255),
        'black': (0,0,0),
        'white': (255,255,255)}
threshanimal = 40
thresh_maxValue = 255
name = ""

# read a reference frame  
frameGray = cv2.imread("mouse2.jpg")
src = cv2.cvtColor(frameGray, cv2.COLOR_BGR2GRAY)

# invert binary
th, dst = cv2.threshold(src, thresh, maxValue, cv2.THRESH_BINARY_INV)
img2 , contours, hierarchy = cv2.findContours(dst,cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
ca = max(contours, key =cv2.contourArea)

M=cv2.moments(ca)
x = int(M['m10']/M['m00'])
y = int(M['m01']/M['m00'])
print("x value is"  + repr(x) + "y value is"  + repr(y))

cv2.drawContours(frameGray, [ca], 0, BGR_COLOR['green'], 2, cv2.LINE_AA)
cv2.circle(frameGray, (x,y), 25, BGR_COLOR['white'], -1)
cv2.namedWindow('image', cv2.WINDOW_NORMAL)
cv2.imshow('image',frameGray)
# save detected animal with centroid
cv2.imwrite('mousedetected_centroid.jpg', frameGray)
cv2.waitKey(0)

cv2.destroyAllWindows()