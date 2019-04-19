from libdw import pyrebase
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
import firebase_admin
from firebase_admin import credentials, firestore

cred=credentials.Certificate("temp.json")
FireBase=firebase_admin.initialize_app(cred)

db=firestore.client()

collection= db.collection(u'user')  #collection



class mainWindow(BoxLayout):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.ids.name.text='Western'
        
    def send_info(self):
        ORDER=self.ids.Order.text
        PHONE=self.ids.Phone.text
        collection.document(ORDER).set(
                {
                 u"Order number":ORDER,
                 u"Phone number":PHONE                     
                        }                               
                )
    
class firebaseApp(App):
    def build(self):
        return mainWindow()
    
if __name__=="__main__":
    display=firebaseApp()
    display.run()






