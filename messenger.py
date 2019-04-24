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
TIMEDIFFERENCE = -8 #The time difference between twilio and Singapore
#===============================================#

class twilio_handler():

    @prints("loading", TWILIO_CREDENTIALS_PATH, "loaded", "ok")
    def __init__(self):
        """
        Initialization of twilio handler class

        Attributes
        ----------
        - self.config       : dict
            Authentication dictionary for twilio interactions
        - self.firebase     : object
            Firebase object
        - self.client       : object
            Twilio object
        - self.running      : bool
            Operational state of class
        """
        #Connect to the twilio API
        with open(TWILIO_CREDENTIALS_PATH, "r") as f:
            self.config = {"account_sid": f.readline().strip(),
                           "auth_token": f.readline().strip(),
                           "sender_number": f.readline().strip()
                           }

        if DEBUG:
            print("[DEBUG] CONFIG:{}".format(self.config))

        #Connect to the firebase
        self.firebase = Firebase()
        self.firebase.connect()

        #Connect to the twilio API
        self.client = Client(self.config['account_sid'],self.config['auth_token'])
        self.running = True
        self.last_message_timing = datetime.datetime.now()
        
#        #print all messages between now and 5 seconds ago
#        messages = self.client.messages.list(date_sent_before=datetime.datetime.now(),
#                                           date_sent_after=datetime.datetime.now() - datetime.timedelta(seconds=5))
#        
#        for record in messages:
#            print(record.body)
#        
#        #print a datetime
#        print(datetime.datetime(2019, 4, 25, 0, 0))
#
        
            
    def get_order(self):
        """
        Method gets order data from database

        Parameters
        ----------
        None

        Calls
        -----
        self.firebase.get_data : Method
            Grabs data from firebase

        Returns
        -------
        self.orders : dict
            Associated orders at current time
        """
        #store the orders for the current cycle inside the class
        self.orders = self.firebase.get_data("orders")

    def parse_orders(self):
        """
        Method to decode data pulled from database

        Parameters
        ----------
        None

        Calls
        -----
        self.get_order      : Method
            Get current orders data
        self.store_order    : Method
            Stores order data
        """
        #save the information from the firebase for this cycle
        self.get_order()
        #Loop through all the stores
        for store_name,store_orders in self.orders.items():
            #Loop through all the orders
            for order_id,order_details in store_orders.items():
                #store order
                self.store_order(store_name,store_orders,order_id,order_details)
                pass

    def store_order(self, store_name, store_orders,\
                    order_id, order_details):
        """
        Method to store order details pulled from firebase

        Parameters
        ----------
        store_name      : string
            Store identification name
        store_orders    : string
            Order Key
        order_id        : string
            Order ID
        order_details   : string
            Order details

        Calls
        -----
        self.create_message : Method
            Creates messages based on details provided
        """
        #store the details of the order in dictionary
        if order_details["ready"] == True:
            print("order number {} is ready".format(order_id))
            #save the information of all customers
            customers_data = self.firebase.get_data("customers")
            message_information = {
                    #store the current information
                    'order_id' : order_id,
                    'store_name' : store_name,
                    'store_orders' : store_orders,
                    'order_details' : order_details,
                    #get the order details
                    'food' : order_details['food'],
                    'persons_id' : order_details['id'],
                    }

            #add the persons details
            customer = customers_data[message_information['persons_id']]
            #print(customer)
            message_information['service'] = customer['service']
            message_information['mobile'] = customer['mobile']

            #If there is additional information, append it. Else, just put NA
            try:
                message_information['addit_info'] = order_details['addit_info']
            except:
                message_information['addit_info'] = 'NA'

            #Create the message
            self.create_message(message_information)

        else:
            # Update time_waited
            if order_details["order_time"] != "None":
                time_elapsed = int(time.time()) - order_details["order_time"]
                self.firebase.update(["orders", STORE_NAME, order_id], {"time_waited": time_elapsed})

    def create_message(self,message_information):
        """
        Method creates message for specified customer

        Parameters
        ----------
        - message_information : dict
            Associated information to be passed into
            notification message for customer

        Calls
        -----
        self.client.messages.create : Method
            Creates message to send to customer
        """

        #create the message
        if message_information['service'] == 'whatsapp':
            #The details of the message sent is saved here
            message = self.client.messages.create(
                          body='Your order of {food} from the {store_name} store is ready. Additional Information: {addit_info}'.format(**message_information),
                          from_='whatsapp:{sender_number}'.format(**self.config),
                          to='whatsapp:{mobile}'.format(**message_information)
                          )
        #Set the ready state to waiting for collection
        #self.firebase.db.child('orders').child('{store_name}'.format(**message_information)).child('{order_id}'.format(**message_information)).update({"ready":"waiting for collection"})
        self.firebase.update(["orders", STORE_NAME, message_information["order_id"]], {"ready": "waiting for collection"})

    #def update_times_waited(self):
        #This class is to update the waiting times as the person waits
    
    def handle_messages(self):
        """
        Method handles incoming messages to the Twilio API
        
        Parameters
        ----------
        None
        
        Calls
        -----
        datetime.datetime.now() : Method
            Gets the current time in the format required by Twilio
        datetime.timedelta(hours = TIMEDIFFERENCE)
            Used the make a time difference in a format that can 
            be added and subtracted from datetime objects
        self.client.messages.create : Method
            Creates message to send to customer
        
        """
        
        #Get the time at which the code started running
        current_time = datetime.datetime.now()
        
        #get all messages between now and the time where a message was last received
        messages = self.client.messages.list(
                                            date_sent_before = datetime.datetime.now()+ datetime.timedelta(hours = TIMEDIFFERENCE),
                                            date_sent_after = self.last_message_timing + datetime.timedelta(hours = TIMEDIFFERENCE)
                                            )
        
        #Iterate through all the new messages
        for record in messages:
            #If it is not from the Twilio Client
            if record.from_ != 'whatsapp:+14155238886':
                #Then update the timing of the last message to the current time
                self.last_message_timing = current_time
                #If the message sent is the '?' that seeks to get the number 
                #of people in the queue
                if record.body == '?':
                    #Get the data about people from firebase
                    people_data = self.firebase.get_data('people_count')
                    #Get the number of people queueing
                    no_of_people = people_data['people_count']
                    #Create a message from the API to tell the person
                    #asking the number of people in the queue
                    message = self.client.messages.create(
                          body='The number of the people in the queue is {}'.format(no_of_people),
                          from_='whatsapp:{sender_number}'.format(**self.config),
                          to=record.from_
                          )         

    def run(self):
        while self.running:
            self.parse_orders()
            self.handle_messages()
            sleep(5)

if __name__ == "__main__":
    a = twilio_handler()
    a.run()
    

