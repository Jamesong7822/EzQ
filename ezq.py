#################################################
# Property of EZQ
# LAST MODIFIED: 220419
#################################################

#################################################
"""
This ezq class is written to modularise the
project
This script runs in the RPI client and does the
following:
    - Connect to firebase using Firebase class
    - Take a snapshot using webcam every set time
      interval
    - Send the img data to firebase
"""
#################################################

#------------------IMPORTS----------------------#
import cv2
import numpy as np
import os
import time

from time import sleep
from firebase import Firebase

#==================CONSTANTS====================#
TEST_IMAGE_PATH="index.jpeg"
CAM=0 # Use 0 for RPI and 1 for PC
UPDATE_RATE = 20 # seconds
RUNFOR = 100000000000 # seconds
#===============================================#

class RPI():

    def __init__(self):
        """
        Initialization of RPI client

        Attributes
        ----------
        - self.firebase     : object
            Firebase object
        - self.last-snap    : int
            Last snaptime
        - self.start_time   : float
            Start time
        - self.cap          : object
            Cv2 VideoCapture object
        - self.done         : bool
            Operational state of client
        """
        # Create a firebase object
        self.firebase = Firebase()

        # Connect to firebase object
        self.firebase.connect()

        # Set up Variables
        self.last_snap = 0
        self.start_time = time.time()

        # Start capture
        self.cap = cv2.VideoCapture(CAM)

        # Set to run
        self.done = False

    def snapshot(self):
        """
        Method takes a snapshot using usb webcam

        Parameters
        ----------
        None

        Returns
        -------
        - img           : array
            Snapshot img array
        - snaptime      : integer
            Time at point of snapshot
        """

        # Takes a snapshot using webcam
        ret, img =  self.cap.read()
        img = cv2.resize(img, None, fx=0.5, fy=0.5 )
        snaptime = int(time.time())
        #print (img_resized.shape)
        #cv2.imshow("Snapshot", img_resized)
        #cv2.waitKey(100)
        #cv2.destroyAllWindows()

        return img, snaptime

    def run(self, type="actual"):
        """
        Method to run operationally

        Parameters
        ----------
        type : string
            Run type input of 'test' or 'actual'
            Defaults 'actual'

        Function Calls
        --------------
        self.done               : bool
            Running state of EzQ client
        self.firebase.update    : Method
            Updates firebase
        self.convert_img_data   : Method
            Converts data to dict form

        Returns
        -------
        None
        """
        assert type in ["actual", "test"], "Please input valid runtype: 'test', 'actual'"

        if type == "actual":
            while not self.done:

                if time.time() - self.start_time > RUNFOR:
                    print ("Ran for {}. Ending Service.".format(RUNFOR))
                    self.done = True

                elif time.time() - self.last_snap > UPDATE_RATE:
                    img, self.last_snap = self.snapshot()
                    img_dict = self.convert_img_data(img)
                    self.firebase.update("image", img_dict)
                    self.firebase.update("snaptime", {"time": self.last_snap})

        else:
            data = cv2.imread(TEST_IMAGE_PATH)
            # print (data.shape)
            data_dict = self.convert_img_data(data)
            self.firebase.update("image", data_dict)

    def convert_img_data(self, img):
        """
        Method converts image data
        to dict format

        Parameters
        ----------
        img : array
            Img array data

        Returns
        -------
        img_dict : dict
            Associated img dictionary data
        """
        img_dict = {}
        if img.shape:
           for row in range(img.shape[0]):
               rowdata = img[row,:]
              # print(len(rowdata))
              # print (rowdata.shape)
               img_dict[row] = np.array2string(rowdata)
        #print (len(img_dict[0]))
        return img_dict

if __name__ == "__main__":
    R = RPI()
    R.run("test")
    cv2.destroyAllWindows()
    R.cap.release()
    elapsed_time = time.time()-R.start_time
    print ("Ran for {:.2f} seconds.".format(elapsed_time))
