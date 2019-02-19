# USAGE
# the video to be analysed  must be stored in the current directory of this code
# the program will automatically read the *.mp4 file and save the final results in the 
# current date folder. Tracking video will be saved in 'timing' sub-folder and 
# final track plot in 'traces' sub-folder. A *.csv file will be created with distance travelled and time taken

import numpy as np
import cv2
import glob, os, sys, time, datetime

ONLINE = True
CALIBRATE = False
RELATIVE_DESTINATION_PATH = str(datetime.date.today()) + "_distance/"
FPS = 10
HD = 1536 , 576

BGR_COLOR = {'red': (0,0,255),
        'green': (127,255,0),
        'blue': (255,127,0),
        'yellow': (0,127,255),
        'black': (0,0,0),
        'white': (255,255,255)}
WAIT_DELAY = 1
threshanimal = 40
thresh_maxValue = 255
name = ""


# function to draw animal trace
def trace(filename):
    global name,WAIT_DELAY
    name = os.path.splitext(filename)[0]
    cap = cv2.VideoCapture(filename)
    h, w = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)), int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    #HD = w , h
    # Take first non-null frame and find corners within it
    ret, frame = cap.read()
    while not frame.any():
        ret, frame = cap.read()
    video = cv2.VideoWriter(RELATIVE_DESTINATION_PATH + 'timing/' + name + "_trace.mp4", cv2.VideoWriter_fourcc(*'H264'), FPS, HD, cv2.INTER_LINEAR)
    imgTrack = np.zeros_like(frame)

    start = time.time()
    distance = _x = _y = 0

    while frame is not None:
        ret, frame = cap.read()
        
        if frame is None:   # not logical
            break
        t = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.
        frameColor = frame.copy()

        frameGray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        kernelSize = (35, 35)
        frameBlur = cv2.GaussianBlur(frameGray, kernelSize, 0)
        _, thresh = cv2.threshold(frameBlur, threshanimal, thresh_maxValue, cv2.THRESH_BINARY_INV)
        _, contours, hierarchy = cv2.findContours(thresh.copy(),cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        if len(contours) < 1:   
            continue

        # Find a contour with the biggest area (animal most likely)
        contour = max(contours, key =cv2.contourArea)
        M = cv2.moments(contour)
        x = int(M['m10']/M['m00'])
        y = int(M['m01']/M['m00'])
        if _x == 0 and _y == 0:
            _x = x
            _y = y
        distance += np.sqrt((x-_x)**2 + (y-_y)**2)
        if ONLINE:
            imgPoints = np.zeros(frame.shape,np.uint8)

            # Draw a contour and a centroid of the animal
            cv2.drawContours(imgPoints, [contour], 0, BGR_COLOR['yellow'], 1, cv2.LINE_AA)
            imgPoints = cv2.circle(imgPoints, (x,y), 25, BGR_COLOR['white'], -1)
            
            # Draw a track of the animal
            imgTrack = cv2.addWeighted(np.zeros_like(imgTrack), 1, cv2.line(imgTrack, (x,y), (_x,_y),
                BGR_COLOR['red'], 1, cv2.LINE_AA), 1, 0.)
            imgContour = cv2.add(imgPoints, imgTrack)

            frame = cv2.bitwise_and(frame, frame, mask = thresh)
            frame = cv2.addWeighted(frame, 0.4, imgContour, 1.0, 0.)

            cv2.putText(frame, "Distance in pixels" + str('%.2f' % distance),
                (10,20), cv2.FONT_HERSHEY_SIMPLEX, 1, BGR_COLOR['white'])
            cv2.putText(frame, "Time " + str('%.0f sec' % (cap.get(cv2.CAP_PROP_POS_MSEC)/1000.)),
                (10,50), cv2.FONT_HERSHEY_SIMPLEX, 1, BGR_COLOR['white'])
            cv2.circle(frame, (x,y), 5, BGR_COLOR['white'], -1, cv2.LINE_AA)
            layout = np.hstack((frame, frameColor))

            cv2.imshow('Home-Cage Trace of ' + name, layout)
            video.write(layout)

            k = cv2.waitKey(WAIT_DELAY) & 0xff
            if k == 27:
                break
            if k == 32:
                if WAIT_DELAY == 1:
                    WAIT_DELAY = 0  # pause
                else:
                    WAIT_DELAY = 1  # play as fast as possible
        _x = x
        _y = y
    cv2.destroyAllWindows()
    cap.release()        

    if ONLINE:
        video.release()
        cv2.imwrite(RELATIVE_DESTINATION_PATH + 'traces/' + name + '_[distance]=%.2f' % distance +
            '_[time]=%.1fs' % t + '.png', imgTrack)

    print(filename + "\tdistance %.2f\t" % distance + "processing/real time %.1f" % float(time.time()-start) + "/%.1f s" % t)
    file.write(name + ",%.2f" % distance + ",%.1f\n" % t)
    file.close()


#for loading video files

if len(sys.argv)>1 and '--online' in sys.argv:
    ONLINE = True
if not os.path.exists(RELATIVE_DESTINATION_PATH + 'traces'):
    os.makedirs(RELATIVE_DESTINATION_PATH + 'traces')
if not os.path.exists(RELATIVE_DESTINATION_PATH + 'timing'):
    os.makedirs(RELATIVE_DESTINATION_PATH + 'timing')
file = open(RELATIVE_DESTINATION_PATH + "distances.csv", 'w')
file.write("animal,distance [pixels],run time [seconds]\n")
file.close()

for filename in glob.glob("*.mp4"):
    file = open(RELATIVE_DESTINATION_PATH + "distances.csv", 'a')
    trace(filename)

