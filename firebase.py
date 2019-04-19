#################################################
# Property of EZQ
# LAST MODIFIED BY: Jamesong7822 @ 030419
#################################################

#################################################
"""
This firebase class is written to modularise the
project.
"""
#################################################

#------------------IMPORTS----------------------#
import os
from time import sleep
from libdw import pyrebase

#-----------------------------------------------#

#=================EDITABLES=====================#
DEBUG = True # turn on/off debugging lines

#=================CONSTANTS=====================#
CREDENTIALS_PATH = "credentials.txt"

#===============================================#

# Decorator
def prints(key1, text1="", key2="", text2=""):
    def wrap(f):
        def wrapper(self, *args):
            print("[{}] {}".format(key1.upper(), text1.upper()))
            res = f(self, *args)
            if key2 != "":
                print("[{}] {}".format(key2.upper(), text2.upper()))

            return res
        return wrapper
    return wrap

class Firebase():

    @prints("loading", CREDENTIALS_PATH, "loaded", "ok")
    def __init__(self):
        # Credentials loading
        with open(CREDENTIALS_PATH, "r") as f:
            self.config = {"databaseURL": f.readline().strip(),
                           "apiKey": f.readline().strip(),
                           }

        if DEBUG:
            print("[DEBUG] CONFIG:{}".format(self.config))

    @prints("connecting", "", "connected")
    def connect(self):
        # Connect to Firebase with loaded Credentials
        self.firebase = pyrebase.initialize_app(self.config)

        # Setup database object
        self.db = self.firebase.database()

    def get_keys(self):
        # Grabs header keys from database object
        keys = [x for x in self.db.child().get().val()]
        if DEBUG:
            print ("[DEBUG] HEADERS: {}".format(keys))
        return keys

    @prints("updating", "", "updated", "ok")
    def update(self, key, data):
        # Updates existing entry in database
        #self.db.child(key).remove()
        self.db.child(key).update(data)

    @prints("Adding", "", "Added", "ok")
    def add(self, key, data):
        # Adds new entry in database
        self.db.child(key).set(data)

    def get_data(self, key):
        # Grabs data from database using specified key
        return self.db.child(key).get().val()

if __name__ == "__main__":
    a = Firebase()
    a.connect()
    data = a.get_data("image")
    #print(data)
