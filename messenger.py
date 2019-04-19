#################################################
# Property of EZQ
# LAST MODIFIED BY: Philip @ 040519
#################################################

#################################################
"""
This twilio class is written to modularise the
project

Requirements: firebase.py by Wei Song
"""
#################################################

#------------------IMPORTS----------------------#
from firebase import Firebase, prints
from twilio.rest import Client

#-----------------------------------------------#

#=================EDITABLES=====================#
DEBUG = True # turn on/off debugging lines
UPDATE_RATE = 60 # seconds


#=================CONSTANTS=====================#
TWILIO_CREDENTIALS_PATH = "twilio_credentials.txt"

#===============================================#

class twilio_handler():

    @prints("loading", TWILIO_CREDENTIALS_PATH, "loaded", "ok")
    def __init__(self):
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

    def get_order(self):
        #store the orders for the current cycle inside the class
        self.orders = self.firebase.get_data("orders")

    def parse_orders(self):
        #save the information from the firebase for this cycle
        self.get_order()
        #Loop through all the stores
        for store_name,store_orders in self.orders.items():
            #Loop through all the orders
            for order_id,order_details in store_orders.items():
                #check order
                self.check_order(store_name,store_orders,order_id,order_details)
                pass

    def check_order(self,store_name,store_orders,order_id,order_details):
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
            print(customer)
            message_information['service'] = customer['service']
            message_information['mobile'] = customer['mobile']

            #If there is additional information, append it. Else, just put NA
            try:
                message_information['addit_info'] = order_details['addit_info']
            except:
                message_information['addit_info'] = 'NA'

            #Create the message
            self.create_message(message_information)

    def create_message(self,message_information):

            #create the message
            if message_information['service'] == 'whatsapp':
                #The details of the message sent is saved here
                message = self.client.messages.create(
                              body='Your order of {food} from the {store_name} store is ready. Additional Information: {addit_info}'.format(**message_information),
                              from_='whatsapp:{sender_number}'.format(**self.config),
                              to='whatsapp:{mobile}'.format(**message_information)
                              )
            #Set the ready state to waiting for collection
            self.firebase.db.child('orders').child('{store_name}'.format(**message_information)).child('{order_id}'.format(**message_information)).update({"ready":"waiting for collection"})

    def run(self):
        while True:
            self.parse_orders()
            sleep(5)

if __name__ == "__main__":
    a = twilio_handler()
    a.run()
