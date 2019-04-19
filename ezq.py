#################################################
# Property of EZQ
# LAST MODIFIED BY: Jamesong7822 @ 030419
#################################################

#################################################
"""
This ezq class is written to modularise the
project
This script runs in the RPI client and does the
following:
    - Connect to firebase using Firebase class
    - Take a snapshot using webcam every set-time
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

#=================+CONSTANTS====================#
TEST_IMAGE_PATH="index.jpeg"
CAM=0 # Use 0 for RPI and 1 for PIC
UPDATE_RATE = 20
RUNFOR = 100000000000
#===============================================#

class RPI():

    def __init__(self):
        # Create a firebase object
        self.firebase = Firebase()
        self.firebase.connect()

        # Set up Variables
        self.last_snap = 0
        self.start_time = time.time()

        # Start capture
        self.cap = cv2.VideoCapture(CAM)

        # Set to run
        self.done = False

    def snapshot(self):
        # Takes a snapshot using webcam
        ret, img =  self.cap.read()
        img_resized = cv2.resize(img, None, fx=0.5, fy=0.5 )
        snaptime = int(time.time())
        #print (img_resized.shape)
        #cv2.imshow("Snapshot", img_resized)
        #cv2.waitKey(100)
        #cv2.destroyAllWindows()

        return img_resized, snaptime

    def run(self):
        while not self.done:

            if time.time() - self.start_time > RUNFOR:
                print ("Ran for {}. Ending Service.".format(RUNFOR))
                self.done = True

            elif time.time() - self.last_snap > UPDATE_RATE:
                self.last_snap = time.time()
                img, snaptime = self.snapshot()
                img_dict = self.convert_data(img)
                self.firebase.update("image", img_dict)
                self.firebase.update("snaptime", {"time": snaptime})

    def convert_data(self, data):
        """
        Method converts image array data
        to uploadable format to firebase
        """
        data_dict = {}
        if data.shape:
           for row in range(data.shape[0]):
               rowdata = data[row,:]
              # print(len(rowdata))
              # print (rowdata.shape)
               data_dict[row] = np.array2string(rowdata)
        #print (len(data_dict[0]))
        return data_dict


    def testrun(self):
        data = cv2.imread(TEST_IMAGE_PATH)
        # print (data.shape)
        data_dict = self.convert_data(data)
        self.firebase.update("image", data_dict)


if __name__ == "__main__":
    R = RPI()
    #R.testrun()
    R.run()
    cv2.destroyAllWindows()
    R.cap.release()
    elapsed_time = time.time-server.start_time
    print ("Ran for {}".format(elapsed_time))
