from libdw import pyrebase
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
import firebase_admin
from firebase_admin import credentials, firestore
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout

class DW(FloatLayout):
    pass

class floatlayoutApp(App):
    
    def build(self):
        return DW()

display = floatlayoutApp()
display.run()







cred=credentials.Certificate("temp.json")
FireBase=firebase_admin.initialize_app(cred)

db=firestore.client()

collection= db.collection(u'user')  #collection
output=collection.document(u'bbfish').get()  # input the next string on the right
username=output.to_dict()['name']



class mainWindow(BoxLayout):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.ids.name.text=username
        
    def send_info(self):
        NAME = self.ids.username.text
        AGE=self.ids.age.text
        collection.document(NAME).set(
                {
                 u"name":NAME,
                 u"age":AGE                     
                        }                               
                )
    
    

class firebaseApp(App):
    def build(self):
        return mainWindow()
    
    
if __name__=="__main__":
    display=firebaseApp()
    display.run()























'''

url = "https://dw-1d-23b1f.firebaseio.com/"
apikey = "AIzaSyA-UsBLa0RCdeCkopX2G_Zk8ztmIh7GZFM"

config = {
    "apiKey": apikey,
    "databaseURL": url,
}

firebase = pyrebase.initialize_app(config)
db = firebase.database()


order_list=[]                              #initialize an empty order list


while True:
    db.child("order").set(order_list)
    order = db.child("order").get()
    
    new_order=input('What is the new order?') #get the new order
    order = db.child("order").get()
    
    if order.val()==None:
        pass                                  #if no order, dont retrieve anything
    else:    
        order_list=sorted(order.val())             #else, get the current order list
    
    order_list.append(new_order)               #add new order into the list  
    order_list=sorted(order_list)
    db.child("order").set(order_list)  #upload the new sorted order list to firebase
    
    '''
