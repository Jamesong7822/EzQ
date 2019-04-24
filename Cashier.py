#################################################
# Property of EZQ
# LAST MODIFIED: 220419
#################################################

#################################################
"""
This Cashier UI class is written to modularise the
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
from firebase import Firebase

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.uix.textinput import TextInput
from kivy.properties import ObjectProperty, StringProperty

#=================+CONSTANTS====================#
os.environ["KIVY_GL_BACKEND"] = "gl"
STORE_NAME = 'Western Food'
#===============================================#

# Setup Firebase instance
FIREBASE = Firebase()
FIREBASE.connect()

class MenuScreen(Screen):
    def __init__(self, **kwargs):
        """
        Initialization of MenuScene as a Screen widget
        
        Attributes
        ----------
        - self.order           : str
            Input order
        - self.state           : str
            State of toggle button
        - self.additional_info : str
            Input additional info for order
        - self.popup           : None
            Class attribute to store popup object
        - self.btns            : list
            List to store all buttons
        - self.firebase        : object
            Firebase object
        """
        super(Screen, self).__init__()
        
        # Set up Variables
        self.order = StringProperty(None)
        self.state = StringProperty(None)
        self.additional_info = StringProperty(None)
        self.popup = None
        self.btns = []
        
        # Create a firebase object
        self.firebase = FIREBASE
        
        # Create ToggleButtons for each dish on the menu, store in the list self.btns and add to layout
        menu_list = ["Chicken Chop Spaghetti", "Grilled Fish Spaghetti", "Chicken Cubes with Rice", "Aglio Olio", "Mexican Chicken Chop", "Chicken Chop with Fries"]
        for i in menu_list:
            btn = ToggleButton(text=i, group="menu", font_size = 20, background_normal='', background_color=[0.96, 0.54, 0.41, 1], markup = True)
            btn.bind(on_press = self.get_order)
            self.btns.append(btn)
            self.grid.add_widget(btn)

    def get_order(self, togglebutton):
        """
        Method to save the order of the customer to send to firebase
        
        Parameters
        ----------
        togglebutton : Widget
            ToggleButton containing choice of order
        
        Function Calls
        --------------
        None
        
        Returns
        -------
        None
        
        """
        
        tb = togglebutton

        self.order = str(tb.text)
        self.state = str(tb.state)

    def get_additional_info(self):
        """
        Method to save the additional information for customer's order
        
        Parameters
        ----------
        None
        
        Function Calls
        --------------
        None
        
        Returns
        -------
        None
        
        """
        self.additional_info = str(self.ids.additional_info_input.text)

    def set_pop_up(self):
        """
        Method to conduct sanity check
        
        Parameters
        ----------
        None
        
        Function Calls
        --------------
        self.popup_layout  : Method
            Generate the popup layout
        self.popup.open    : Method
            Opens a popup
        
        Returns
        -------
        None
        
        """
        content = self.popup_layout()
        if not self.popup:
            self.popup = Popup(title="Warning", content=content, auto_dismiss=True, size_hint=(0.5, 0.5))
        self.popup.open()

    def popup_layout(self):
        """
        Method to add neccessary warning and widget to popup
        
        Parameters
        ----------
        None
        
        Function Calls
        --------------
        None
        
        Returns
        -------
        layout   : BoxLayout
            Layout of text and button
        
        """
        layout = BoxLayout(orientation="vertical")
        text = Label(text="Please select an order")
        btn = Button(text="OKAY!")
        btn.bind(on_release=self.close_popup)
        layout.add_widget(text)
        layout.add_widget(btn)
        return layout

    def close_popup(self, *args):
        self.popup.dismiss()

    def check_order(self):
        """
        Method to confirm your order and transit to Submit Screen
        
        Parameters
        ----------
        None
        
        Function Calls
        --------------
        self.set_pop_up   : Method
            Method to conduct sanity check
        self.manager.ids.submit_screen.update_nums_layout : Method
            List out available phone numbers that has not been assigned orders
            
        Returns
        -------
        None
        
        """
        if self.state != "down":
            self.set_pop_up()   

        else:
            self.reset()
            self.manager.current = "SubmitScreen"
            self.manager.ids.submit_screen.update_nums_layout()
            self.manager.ids.submit_screen.order = self.order
            self.manager.ids.submit_screen.additional_info = self.additional_info


    def reset(self):
        """
        Method to reset the state of all Toggle Buttons and Text Input
        
        """
        for i in self.btns:
            if i.state == "down":
                i.state = "normal"
        self.ids.additional_info_input.text = ""


class SubmitScreen(Screen):
    order = StringProperty()
    additional_info = StringProperty()

    def __init__(self, **kwargs):
        """
        Initialization of SubmitScreen as a Screen widget
        
        Attributes
        ----------
        - self.firebase        : object
            Firebase object
        - self.nums            : array
            Array of phone numbers
        - self.num             : str
            Phone number of customer
        - self.state           : str
            State of toggle button
        - self.popup           : None
            Class attribute to store popup object
        - self.nums_btns            : list
            List to store all buttons

        """
        super(Screen, self).__init__()
        self.firebase = FIREBASE
        self.nums = None
        self.num = StringProperty(None)
        self.state = StringProperty(None)
        self.popup = None
        self.nums_btns = []


    def get_nums(self):
        """
        Method to get the phone numbers that has not been served
        
        Parameters
        ----------
        None
        
        Function Calls
        --------------
        self.firebase.get_data   : Method
            Obtain customers data
            
        Returns
        -------
        self.nums  : array
            Array containing phone numbers
        """
        # Clear pre-existing widgets
        if self.nums_btns:
            for x in self.nums_btns:
                self.ids.boxy.remove_widget(x)

        # Get data from database
        data = self.firebase.get_data("customers")
        #print(data)

        # Get keys - order nums
        key = []
        for customer_id,customer in data.items():
            if customer['served'] == False:
                key.append(customer_id)
#        key = [x for x in data]

        # Sort the keys list
        sorted(key, reverse=True)

        # Get the top 3 numbers based on top 3 keys
        self.nums = []
        for k in key:
            d = data[k]
            self.nums.append(k + ':' + d['mobile'])
#        self.nums = [x["mobile"] for x in [data[y] for y in key[:3]]]

        return self.nums

    def bind_nums(self, togglebutton):
        """
        Method to save the selected number and customer id
        """
        tb = togglebutton
        self.num = str(tb.text)
        self.state = str(tb.state)
        self.customer_id = tb.text.split(':')[0]

    def update_nums_layout(self):
        """
        Method to update the available numbers on the screen
        
        Parameters
        ----------
        None
        
        Function Calls
        --------------
        self.get_nums   : Method
            Get the phone numbers that has not been served
        self.bind_nums  : Method
            Save the selected number and customer id
        """
        self.nums = self.get_nums()
        for num in self.nums:
            btn = ToggleButton(text=num, group="nums")
            btn.bind(on_press=self.bind_nums)
            self.nums_btns.append(btn)
            self.ids.boxy.add_widget(btn)

    def set_pop_up(self):
        """
        Method to conduct sanity check
        
        Parameters
        ----------
        None
        
        Function Calls
        --------------
        self.popup_layout  : Method
            Generate the popup layout
        self.popup.open    : Method
            Opens a popup
        
        Returns
        -------
        None
        
        """
        content = self.popup_layout()
        if not self.popup:
            self.popup = Popup(title="Warning", content=content, auto_dismiss=True, size_hint=(0.5, 0.5))
        self.popup.open()

    def popup_layout(self):
        """
        Method to add neccessary warning and widget to popup
        
        Parameters
        ----------
        None
        
        Function Calls
        --------------
        None
        
        Returns
        -------
        layout   : BoxLayout
            Layout of text and button
        
        """
        layout = BoxLayout(orientation="vertical")
        text = Label(text="Please select a number")
        btn = Button(text="OKAY!")
        btn.bind(on_release=self.close_popup)
        layout.add_widget(text)
        layout.add_widget(btn)
        return layout

    def update(self):
        """
        Method to send order data to firebase
        
        Parameters
        ----------
        None
        
        Function Calls
        --------------
        self.firebase.get_data  : Method
            Get order data from firebase
        self.firebase.update    : Method
            Update information on firebase
        
        Returns
        -------
        None
        
        """
        # Get the current order ids
        order_data = self.firebase.get_data("orders")
        store_order_data = order_data[STORE_NAME]
        
        # Used ids
        used_ids = []
        for order_id,item in store_order_data.items():
            used_ids.append(order_id)
        new_id = None
        for i in range(1,999):
            i = '{:0>3}'.format(str(i))
            if i not in used_ids:
                new_id = i
                break
        new_order_dict = {}
        new_order_dict['food'] = self.order
        new_order_dict['ready'] = False
        new_order_dict['addit_info'] = self.additional_info
        new_order_dict['time_waited'] = 0
        new_order_dict['id'] = self.customer_id
        new_order_dict["order_time"] = int(time.time())
        print('adding new id ' + str(new_id) + ' and data ' + str(new_order_dict))
        self.firebase.update(["orders", STORE_NAME], {new_id:new_order_dict})
        #update that the customer is served
        self.firebase.update(["customers",self.customer_id],{'served':True})
        

    def check_nums(self):
        """
        Method to confirm your order and transit to Menu Screen
        
        Parameters
        ----------
        None
        
        Function Calls
        --------------
        self.set_pop_up   : Method
            Method to conduct sanity check
        self.update : Method
            Send order data to firebase
            
        Returns
        -------
        None
        
        """
        if self.state != "down":
            self.set_pop_up()

        else:
            self.update()
            self.manager.current = "MenuScreen"
            #self.manager.ids.submit_screen.order = self.order
            #self.manager.ids.submit_screen.additional_info = self.additional_info

    def close_popup(self, *args):
        self.popup.dismiss()


class CashierApp(App):

    def __init__(self):
        super().__init__()
        self.firebase = FIREBASE

    def build(self):
        pass

if __name__ == "__main__":
    a = CashierApp()
    a.run()
