# USAGE
# python Animal_motion_detector.py
# python Animal_motion_detector.py --video videos/mouse_01.mp4

# Uncomment the following lines to activate virtualenv for current interpreter 
# only if openCV is installed in virtual environment named'cv'
# activate_this = '/home/pi/.virtualenvs/cv/bin/activate_this.py'
# with open(activate_this) as file_:
    # exec(file_.read(), dict(__file__=activate_this))

# import the necessary packages
import argparse
import datetime
import imutils
import time, datetime, os, sys
import cv2
import numpy as np

movm = 0

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", help="path to the video file")
ap.add_argument("-a", "--min-area", type=int, default=50, help="minimum area size")
#default 50
args = vars(ap.parse_args())
HD = 768 , 576

# if the video argument is None, then we are reading from webcam
if args.get("video", None) is None:
	camera = cv2.VideoCapture(0)
	time.sleep(0.25)

# otherwise, we are reading from a video file
else:
	camera = cv2.VideoCapture(args["video"])
	tot_f_num = int(camera.get(cv2.CAP_PROP_FRAME_COUNT))
	frame_rate_vid = int(camera.get(cv2.CAP_PROP_FPS))

# initialize the first frame in the video stream
firstFrame = None
avg = None

# loop over the frames of the video
while True:
	# grab the current frame and initialize the Moving/Not Moving
	# text
	start = time.time()
	(grabbed, frame) = camera.read()
	
	text = "Not Moving"
    # if the frame could not be grabbed, then we have reached the end
	# of the video
	if not grabbed:
		break

	# resize the frame, convert it to grayscale, and blur it
	frame = imutils.resize(frame, width=400)
	#width 400
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	gray = cv2.GaussianBlur(gray, (21, 21), 0)
	#pfq += 1
        
	# if the average frame is None, initialize it
	if avg is None:
		print( "[INFO] starting background model...")
		avg = gray.copy().astype("float")
		#rawCapture.truncate(0)
		continue
	# accumulate the weighted average between the current frame and
	# previous frames, then compute the difference between the current
	# frame and running average
	cv2.accumulateWeighted(gray, avg, 0.5)
	frameDelta = cv2.absdiff(gray, cv2.convertScaleAbs(avg))
	thresh = cv2.threshold(frameDelta, 5, 255, cv2.THRESH_BINARY)[1]
	# frame delta 5

	# dilate the thresholded image to fill in holes, then find contours
	# on thresholded image
	thresh = cv2.dilate(thresh, None, iterations=2)
	cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	cnts = cnts[0] if imutils.is_cv2() else cnts[1]
	# loop over the contours
	for c in cnts:
		# if the contour is too small, ignore it
		if cv2.contourArea(c) < args["min_area"]:
			continue

		# compute the bounding box for the contour, draw it on the frame,
		# and update the text
		(x, y, w, h) = cv2.boundingRect(c)
		cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
		text = "Moving"

	# draw the text and timestamp on the frame
	cv2.putText(frame, "Animal Status: {}".format(text), (10, 20),
		cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
	cv2.putText(frame, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),
		(10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 255, 0), 1)
	print("time taken:"+repr(time.time()-start))
	if text == "Moving":
                movm +=1

    # show the frame 
	cv2.imshow("Animal video", frame)
	# uncomment the next line if you want to save the video for visualization later
	#video.write(frame)
	key = cv2.waitKey(1) & 0xFF

	# if the `q` key is pressed, break from the lop
	if key == ord("q"):
		break

        
# cleanup the camera and close any open windows
camera.release()
cv2.destroyAllWindows()
