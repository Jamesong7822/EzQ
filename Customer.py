#################################################
# Property of EZQ
# LAST MODIFIED BY: Jamesong7822 @ 030419
#################################################

#################################################
"""
This customer UI class is written to modularise the
project
This script runs in the RPI client and does the
following:
    - Connect to firebase using Firebase class
    - Collects Customer Contact Details
    - Updates relevant Firebase data
"""
#################################################

#------------------IMPORTS----------------------#
import os
import time
import json

from time import sleep
from firebaseclass import Firebase

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.uix.image import Image

#=================+CONSTANTS====================#
os.environ["KIVY_GL_BACKEND"] = "gl"
#===============================================#


class OrderScreen(Screen):

    def __init__(self, **kwargs):
        super(Screen, self).__init__()
        self.popup = None

#    def update_order(self, instance):
#        self.ids.Order.text += instance.text
#        self.Label.text += instance.text

    def update_phone(self, instance):
        self.ids.Phone.text += instance.text
        self.Label.text += instance.text

    def keypad(self, title):
        layout = BoxLayout(orientation="vertical")
        # Generate Label
        text = ''
        if self.ids.Phone.on_touch_down:
            if self.ids.Phone.text != '':
                text = self.ids.Phone.text

        self.Label = Label(text=text, size_hint=(1, 0.2))
        layout.add_widget(self.Label)

        # Generate Keypad
        keypad = GridLayout(rows=4, cols=3)
        for num in [1,2,3,4,5,6,7,8,9,"X",0, "Enter"]:
            btn = Button(text=str(num), id=str(num))
            if num == "Enter":
                btn.bind(on_press=self.close_popup)

            elif num == "X":
                if title == "Order Number":
                    btn.bind(on_press=self.delete_order_input)
                elif title == "Phone Number":
                    btn.bind(on_press=self.delete_phone_input)

            else:
                if title == "Order Number":
                    btn.bind(on_press=self.update_order)
                elif title == "Phone Number":
                    btn.bind(on_press=self.update_phone)
            keypad.add_widget(btn)
        layout.add_widget(keypad)


        return layout

    def set_pop_up(self, title):
        content = self.keypad(title)
        if not self.popup:
            self.popup = Popup(title=title,
                               content=content,
                               auto_dismiss=True,
                               size_hint=(0.8,0.8))
        else:
            self.popup.title = title
            self.popup.content = content
        self.popup.open()

#    def delete_order_input(self, instance):
#        text = self.ids.Order.text
#        self.ids.Order.text = text[:-1]
#        self.Label.text = self.Label.text[:-1]

    def delete_phone_input(self, instance):
        text = self.ids.Phone.text
        self.ids.Phone.text = text[:-1]
        self.Label.text = self.Label.text[:-1]

    def close_popup(self, instance):
        self.popup.dismiss()

class SubmitScreen(Screen):
    pass


class CustomerApp(App):

    def __init__(self):
        super().__init__()
        self.firebase = Firebase()
        self.firebase.connect()

    def update(self, type):
        app = App.get_running_app()
        self.root.ids.Order.text = "HI"

    def send_info(self, phone):
        exists = False
#        customer_data = {str(ordernum): str(phone)}
#        self.firebase.update("new_customers", customer_data)
        customer_data = self.firebase.get_data("customers")
        print(customer_data)
        used_ids = []
        for customer_id, customer_data in customer_data.items():
            #check if the mobile number exists yet            
            if customer_data['mobile'] == '+65' + phone: 
                #update db
                customer_data["served"] = False
                self.firebase.db.child('customers').child(customer_id).update(customer_data)
                exists = True
                break
            #if not,
            else:
                used_ids.append(customer_id)
        
        new_id = None
        if exists == False:
            #the phone number is new
            for i in range(1,999):
                i = '{:0>3}'.format(str(i))
                if i not in used_ids:
                    new_id = i
                    break
            #update db
            customer_dict = {'mobile': '+65' + phone, "served": False, 'service': "whatsapp"}
            self.firebase.db.child('customers').child(new_id).update(customer_dict)
        

    def build(self):
        pass

if __name__ == "__main__":
    a = CustomerApp()
    a.run()
