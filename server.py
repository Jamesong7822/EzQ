#################################################
# Property of EZQ
# LAST MODIFIED: 220419
#################################################

#################################################
"""
This server class is written to modularise the
project.
This server class will be runned on the cloud or
local platform with sufficient computing power
for image dectection requirements for EzQ service.
This script runs in the cloud/computer server and
does the following:
    - Connect to firebase using Firebase class
    - Retrieve a snapshot from Firebase at defined
      Update Frequency
    - Parse the image through Darknet and update
      Firebase on the current queue length

"""
#################################################

#------------------IMPORTS----------------------#
import os
import numpy as np
import cv2
import re
import time

from firebase import prints

from time import sleep
from firebase import Firebase
#-----------------------------------------------#

#-----------------YOLO IMPORTS------------------#
from pydarknet import Detector, Image

#=================EDITABLES=====================#
DEBUG = True # turn on/off debugging lines
UPDATE_RATE = 30 # seconds
RUNFOR = 1000

# CV2 TUNABLES
SCREEN_SIZE = (640, 480)
TITLE = "EzQ People Count"
RECT_COLOR = (0, 255, 0) # Green
RECT_THICKNESS = 1

#================YOLO CONSTANTS=================#
YOLOV3_PATH = "YOLO3-4-Py/cfg/yolov3.cfg"
#YOLOV3_PATH = "YOLO3-4-Py/cfg/yolov3-tiny.cfg"
WEIGHTS_PATH = "YOLO3-4-Py/weights/yolov3.weights"
#WEIGHTS_PATH = "YOLO3-4-Py/weights/yolov3-tiny.weights"
COCO_DATA_PATH = "YOLO3-4-Py/cfg/coco.data"
ENCODING = "utf-8"
#===============================================#

class EzQServer():

    def __init__(self):
        """
        Initialization of EzQServer

        Attributes
        ----------
        self.firebase   : object
            Firebase object
        self.screen_w   : integer
            Associated screen width
        self.screen_h   : integer
            Associated screen height
        self.done       : bool
            Operational state of EzQServer
        self.start_time : float
            Start time of EzQServer service
        self.raw_image  : None
            Raw Image variable
        self.snaptime   : None
            Snaptime

        Calls
        -----
        - self.firebase.connect     : Method
            Connect to Firebase databse
        - self.load_darknet         : Method
            Loads darknet for detection service
        - self.namedWindow          : Method
            Sets window title
        - self.resizeWindow         : Method
            Sets window size
        """
        print ("Hello, I am EZQ Server, your one-stop helper in queue-order optimizations!")

        # Connect to firebase
        self.firebase = Firebase()
        self.firebase.connect()

        # Load detection module
        self.load_darknet()

        # Init Variables
        self.screen_w = SCREEN_SIZE[0]
        self.screen_h = SCREEN_SIZE[1]
        self.done = False
        self.start_time = time.time()
        self.raw_image = None
        self.snaptime = None

        # Create Window
        cv2.namedWindow(TITLE, cv2.WINDOW_NORMAL)

        # Resize Window
        cv2.resizeWindow(TITLE, self.screen_w, self.screen_h)

    def extract_data(self, data):
        """
        Method coverts pulled data to array

        Parameters
        ----------
        - data : list
            Pulled data from the list

        Returns
        -------
        - data : array
            Associated array data
        """
        #print (type(data))
        #print(data[0])
        extract = []
        for x in data:
            pixel_rgb = [part.strip("[]") for part in re.split("[\[\]]", x) if part.strip()]
            row_rgb = [x.split() for x in pixel_rgb]
            # row_rgb = [int(y) for y in x for x in row_rgb]
            #row = [re.sub("[^0-9+] ", "", char) for char in x.split()\
                   #if char not in ["[", "]", "\n"]]

            extract.append(row_rgb)
        #print(extract[0])

        return np.uint8(extract)

    def pull_snaptime(self):
        """
        Method gets snaptime and updates self.snaptime

        Parameters
        ----------
        None

        Returns
        -------
        self.snaptime : integer
            Last snaptime as per record on database
        """
        self.snaptime = self.firebase.get_data("snaptime")["time"]

    @prints("pulling", "firebase image", "pulled", "ok")
    def pull_image(self):
        """
        Method pulls image data

        Parameters
        ----------
        None

        Calls
        -----
        - self.firebase.get_data    : Method
            Grabs image data
        - self.extract_data         : Method
            Converts pulled image data to array

        Returns
        -------
        - image_data                : array
            Raw image data
        Pulls image array from firebase
        """
        image = self.firebase.get_data("image")
        # While image data does not exist, pull it
        while not image:
            image = self.firebase.get_data("image")

        self.last_pull = time.time()
        image_data = self.extract_data(image)

        return image_data

    def load_darknet(self):
        """
        Method loads darknet detection module

        Parameters
        ----------
        None

        Calls
        -----
        Detector : Class
            Detector class

        Returns
        -------
        None
        """
        self.net = Detector(bytes(YOLOV3_PATH, encoding=ENCODING),\
                            bytes(WEIGHTS_PATH, encoding=ENCODING),0,\
                            bytes(COCO_DATA_PATH, encoding=ENCODING),\
                                )
    @prints("Detecting", "Pulled Image", "detected", "ok")
    def detect(self, image):
        """
        Method applies detection on image

        Parameters
        ----------
        - image : array
            Image data

        Calls
        -----
        - Image : class
            Image conversion class to convert image
            to correct format for detection
        - self.net.detect : Method
            Method for detecting
        - self.draw_rects : Method
            Draws bounding boxes for detected objects

        Returns
        -------
        - img_copy : Array
            Copy of image with rects drawn on
            for display purposes
        - people_count : Integer
            Associated detected people count
        """
        # Convert image to specific format for darknet processing
        darknet_image = Image(image)
        results = self.net.detect(darknet_image)

        # Create a copy of pulled image
        img_copy = image.copy()
        people_count = 0
        for result in results:
            #print(result)
            #print(result[0]).decode(ENCODING)

            if result[0].decode(ENCODING) == "person":
                people_count += 1
                rects = result[2]
                img_copy = self.draw_rects(img_copy, rects)

        return img_copy, people_count

    def draw_rects(self, image, rects):
        """
        Method draws bounding boxes

        Parameters
        ----------
        - image : array
            Image to draw rect on
        - rects : tuple
            Bounding box data (centerx, centery, width, height)

        Returns
        -------
        - img : array
            Associated image after bounding boxes are drawn on
        """
        x, y, w, h = rects
        img = cv2.rectangle(image, (int(x-w/2),int(y-h/2)),(int(x+w/2),int(y+h/2)), RECT_COLOR, RECT_THICKNESS)

        return img

    def update(self):
        """
        Method updates current image and respective
        class attributes

        Parameters
        ----------
        None

        Calls
        -----
        - self.pull_snaptime : Method
            Get snaptime of image
        - self.pull_image : Method
            Get image
        - server.detect : Method
            Get detection

        Returns
        -------
        self.detect_img : array
            Image with bounding rects
        """
        self.pull_snaptime()
        self.raw_image = self.pull_image()
        lag_time = time.time() - self.snaptime
        start_time = time.time()
        self.detect_img, self.people_count = server.detect(self.raw_image)
        end_time = time.time()
        print ("Detection took {} seconds".format(end_time - start_time))
        print ("{} People Detected in Queue {} Seconds ago".format(self.people_count, lag_time))

        # Update firebase people count
        self.firebase.update("people_count", {"people_count": self.people_count})

    def show_detections(self):
        """
        Method is called to show detected image

        Parameters
        ----------
        None

        Returns
        -------
        - img : cv2 object
            Detection image
        """
        cv2.imshow(TITLE, self.detect_img)

    def run(self):
        """
        Method runs script in sequence

        Parameters
        ----------
        None

        Calls
        -----
        self.update : Method
            Updates current image and respective class attributes
        self.show_detections : Method
            Shows detection image

        """
        # At first run
        if self.raw_image is None:
            self.update()

        # Show detected image
        self.show_detections()

    def testrun(self):
        self.raw_image = server.pull_image()
        start_time = time.time()
        self.detect_img, self.people_count = server.detect(img)
        end_time = time.time()
        print ("That took {} seconds".format(end_time - start_time))
        print ("{} People Detected in Queue".format(self.people_count))
        cv2.imshow("Frame", self.detect_img)
        cv2.waitKey(0)

if __name__ == "__main__":
    server = EzQServer()
    while not server.done:
        server.run()
        key = cv2.waitKey(500) # Update every 500ms
        if time.time() - server.start_time > RUNFOR:
            print ("Ran for {}. Ending Service.".format(RUNFOR))
            server.done = True

        elif time.time() - server.last_pull > UPDATE_RATE:
            #print ("UPDATE")
            server.update()

    #server.testrun()
    cv2.destroyAllWindows()

## TO DO:
"""
Rewrite 'run' method, 'pull_img' method shud update an attribute
that 'show_detections' can be opencved in a loop
"""
