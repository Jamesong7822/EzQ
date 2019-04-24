#################################################
# Property of EZQ
# LAST MODIFIED: 220419
#################################################

#################################################
"""
This firebase class is written to modularise the
project.

This script is used as an import for database
updating functionalities required by EzQ service.
It has the following methods:
    - connect: Connect to firebase
    - get_keys: Get top level keys
    - update: Update entry in firebase
    - get_data: Pulls data from firebase
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
        """
        Initialization of firebase class

        Attributes
        ----------
        self.config         : dict
            Config details to authenticate firebase
        """
        # Credentials loading
        with open(CREDENTIALS_PATH, "r") as f:
            self.config = {"databaseURL": f.readline().strip(),
                           "apiKey": f.readline().strip(),
                           }

        if DEBUG:
            print("[DEBUG] CONFIG:{}".format(self.config))

    @prints("connecting", "", "connected")
    def connect(self):
        """
        Method connects to firebase database

        Returns
        -------
        - self.firebase     : object
            Firebase object
        - self.db           : object
            Database object
        """
        # Connect to Firebase with loaded Credentials
        self.firebase = pyrebase.initialize_app(self.config)

        # Setup database object
        self.db = self.firebase.database()

    def get_keys(self):
        """
        Method grabs keys from database

        Returns
        -------
        - keys      : list
            Associated header keys in database
        """
        # Grabs header keys from database object
        keys = [x for x in self.db.child().get().val()]
        if DEBUG:
            print ("[DEBUG] HEADERS: {}".format(keys))
        return keys

    @prints("updating", "", "updated", "ok")
    def update(self, keys, data):
        """
        Method updates existing entry in database

        Parameters
        ----------
        - keys       : list
            Key(s) to update database with
        - data      : dict
            Associated data to update database with

        Returns
        -------
        None
        """
        # Updates existing entry in database
        #self.db.child(key).remove()
        if isinstance(keys, str):
            self.db.child(keys).update(data)
        else:
            key = "/".join(keys)
            self.db.child(key).update(data)

    def remove_data(self, key):
        """
        Method removes data from selected key
        in database

        Parameters
        ----------
        - key : string
            key of target data

        Returns
        -------
        None
        """

        return self.db.child(key).remove()

    def get_data(self, key):
        """
        Method grabs data from selected key
        in database

        Parameters
        ----------
        - key       : string
            Key to pull data from

        Returns
        -------
        - data      : dict
            Associated data from input key
            in database
        """
        # Grabs data from database using specified key
        return self.db.child(key).get().val()

if __name__ == "__main__":
    a = Firebase()
    a.connect()
    data = a.get_data("image")
