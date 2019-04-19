from libdw import pyrebase
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
import firebase_admin
from firebase_admin import credentials, firestore

cred=credentials.Certificate("temp.json")
FireBase=firebase_admin.initialize_app(cred)

while True:  #infinite loop

    db=firestore.client()
    
    collection= db.collection(u'user')  #collection
    
    order_num=input('Please input the order number')
    
    output = collection.document(order_num).get() # This will return you a Google cloud object
    phone_num = output.to_dict()['Phone number'] # use .to_dict() method to convert output to a python dictionary
    print('we will send a message to '+phone_num+' through twilio')
    
    



    