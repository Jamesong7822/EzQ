# -*- coding: utf-8 -*-
"""
Created on Wed Apr 24 13:22:34 2019

@author: Philip
"""

#################################################
# Property of EZQ
# LAST MODIFIED: 220419
#################################################

#################################################
"""
This twilio class is written to modularise the
project.

This script is used as an import for messenging
functionalities required by the EzQ service.
It has the following methods:
    - get_order : get orders from database
    - parse_orders : decode orders from database
    - store_order : store order details locally
    - create_message : create message object
    - run : run the entire system

Requirements: firebase.py by Wei Song
"""
#################################################

#------------------IMPORTS----------------------#
from firebase import Firebase, prints
from twilio.rest import Client
from time import sleep
import time
import datetime

#-----------------------------------------------#

#=================EDITABLES=====================#
DEBUG = True # turn on/off debugging lines
UPDATE_RATE = 60 # seconds


#=================CONSTANTS=====================#
TWILIO_CREDENTIALS_PATH = "twilio_credentials.txt"
STORE_NAME = "Western Food"
#===============================================#

x = datetime.datetime.now() - datetime.timedelta(minutes=5)
y = datetime.datetime.now()

print(x,y)