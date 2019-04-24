#################################################
# Property of EZQ
# LAST MODIFIED: 220419
#################################################

#################################################
"""
This chefgui class is written to modularise the
project.
This script runs to update chef on orders and does
the following:
    - Connect to firebase using Firebase class
    - Pull order data from firebase
    - Update state of order preparation
        - False                     : Order queued
        - True                      : Order completed
        - Waiting for collection    : Order notification sent
"""
#################################################


#------------------IMPORTS----------------------#
import os
import time
import json

from time import sleep
from firebase import Firebase

#---------------KIVY IMPORTS--------------------#
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
from kivy.clock import Clock

#==================CONSTANTS====================#
os.environ["KIVY_GL_BACKEND"] = "gl"
STORE_NAME = 'Western Food'
#===============================================#

# Setup Firebase instance
FIREBASE = Firebase()
FIREBASE.connect()

class  StartScreen(Screen):
    pass

#This screen is just a buffer to update that it is done
class OrderDoneScreen(Screen):

    def __init__(self, **kwargs):
        """
        Initialize OrderDoneScreen

        Parameters
        ----------
        Screen : Screen Object

        Returns
        -------
        None
        """
        #Init the parent class
        super(Screen, self).__init__()
#        self.manager.current = "OrderCompletionScreen"
#        self.go_back()

    def event(self):
        """
        Schedule one time event

        Parameters
        ----------
        None

        Calls
        -----
        - Clock.schedule_once : Method
            Schedules self.go_back method once

        Returns
        -------
        - None
        """
        Clock.schedule_once(self.go_back, 2)

    def go_back(self, *dt):
        """
        Method changes current screen and updates orders

        Parameters
        ----------
        - *dt : time object
            Clock - time object

        Calls
        -----
        - update_orders_layout() : Method
            Update orders

        Returns
        -------
        None
        """

        self.manager.ids.order_completion_screen.update_orders_layout()
        self.manager.current = "OrderCompletionScreen"


class OrderCompletionScreen(Screen):
    # Declare property objects
    order = StringProperty()
    additional_info = StringProperty()

    def __init__(self, **kwargs):
        """
        Instantiates Order Completion Screen

        Attributes
        ----------
        - self.firebase     : object
            Firebase object
        - self.datas         : list
            Init datas storage attribute
        - self.num          : None
            Sets class attribute to a string property
        - self.state        : None
            Sets class attribute to a string property
        - self.popup        : None
            Init class attribute to store popup object
        - self.order_btns   : list
            Init list to store order buttons objects
        - self.first_run    : bool
            Set first_run attribute to True at startup
        """
        print('INITING ORDER COMPLETION SCREEN')
        super(Screen, self).__init__()
        self.firebase = FIREBASE
        self.datas = []
        self.num = StringProperty(None)
        self.state = StringProperty(None)
        self.popup = None
        self.order_btns = []
        self.first_run = True

    def get_orders(self):
        """
        Method to pull order datas from firebase

        Parameters
        ----------
        None

        Calls
        -----
        - self.firebase.get_data : Method
            Pulls order data from firebase

        Returns
        -------
        - self.datas : list
            Store info to display on button widget
        """
        print('GETTING NUMS')

        data = self.firebase.get_data("orders")
        print(data)
        # Get particular data for store
        store_data = data[STORE_NAME]

        # Get keys - order nums
        # We only want the keys of those whose food ready is false
        key = []
        for order_id, order in store_data.items():
            if order['ready'] == False:
                key.append(order_id)
                print(order_id)

        # Sort the keys list
        sorted(key, reverse=True)

        # List all the uncompleted orders
        self.datas = []
        for k in key:
            d = store_data[k]
            self.datas.append(k + ':' + d['food'] + ' ' + d['addit_info'] + ' ' + str(d['time_waited']))
#        self.nums = [x["mobile"] for x in [data[y] for y in key[:3]]]

        return self.datas

    def bind_nums(self, togglebutton):
        """
        Method callback for togglebutton widget

        Parameters
        ----------
        - togglebutton : object
            ToggleButton widget

        Calls
        -----
        - self.check_orders : Method
            Updates firebase and resets current widgets
        """
        tb = togglebutton
        self.num = str(tb.text)
        self.state = str(tb.state)
        self.selected_order_id = tb.text.split(':')[0]
        self.check_orders()

    def start(self):
        """
        Method startups the app

        Parameters
        ----------
        None

        Calls
        -----
        - self.update_orders_layout : Method
            Updates orders layout
        - Clock.schedule_interval   : Method
            Set up an interval event
        """
        if self.first_run:
            # Update screen layout
            self.update_orders_layout()
            # Updates first_run attribute to false
            self.first_run = False
            # Schedule event
            Clock.schedule_interval(self.update_orders_layout, 3)

    def update_orders_layout(self, *dt):
        """
        Method generates order layout

        Parameters
        ----------
        - *dt : object
            Time object from Clock

        Calls
        -----
        - self.get_orders : Method
            Get order data from firebase
        - clear_widgets   : Method
            Clear widgets in identified widget group

        """
        self.datas = self.get_orders()
        self.ids.boxy.clear_widgets()

        # Loop through data in self.datas list
        for data in self.datas:
            # Create togglebutton widget
            btn = ToggleButton(text=data, group="nums", font_size="25dp")
            # Bind callback to btn
            btn.bind(on_press=self.bind_nums)
            # Add button object reference to list
            self.order_btns.append(btn)
            # Add button widget to layout
            self.ids.boxy.add_widget(btn)
            # print(self.order_btns)

    def set_pop_up(self):
        """
        Method sets up popup object

        Parameters
        ----------
        None

        Calls
        -----
        - self.popup_layout : Method
            Generates popup layout

        Returns
        -------
        None
        """
        # Generate popup layout
        content = self.popup_layout()
        if not self.popup:
            # Create popup if it doesnt exist yet
            self.popup = Popup(title="Warning", content=content, auto_dismiss=True, size_hint=(0.5, 0.5))

        # Else just open popup
        self.popup.open()

    def popup_layout(self):
        """
        Method creates popup layout

        Parameters
        ----------
        None

        Calls
        -----
        None

        Returns
        -------
        - layout : object
            Layout object
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
        Method to update

        Parameters
        ----------
        None

        Calls
        -----
        - self.firebase.get_data : Method
            Get order data from firebase

        Returns
        -------
        None
        """
        # Get the current order ids
        order_data = self.firebase.get_data("orders")
        store_order_data = order_data[STORE_NAME]

#        try:
        order_data = self.firebase.get_data("orders")
        store_order_data = order_data[STORE_NAME]
        customer_id = store_order_data[self.selected_order_id]['id']
#            try:
        customer_data = self.firebase.get_data("customers")
        phone_num = customer_data[customer_id]['mobile']
        print('we will send a message to ' + phone_num + ' through twilio')
        # Updates firebase
        self.firebase.db.child('orders').child('{}'.format(STORE_NAME)).child('{}'.format(self.selected_order_id)).update({"ready":True})

    def reset(self):
        """
        Resetting method

        Parameters
        ----------
        None

        Calls
        -----
        - remove_widget : Method
            Remove target widgets from identified layout

        Returns
        -------
        None
        """
        for i in self.order_btns:
           self.ids.boxy.remove_widget(i)

    def check_orders(self):
        """
        Method to check order data

        Calls
        -----
        - self.set_pop_up           : Method
            Sets up popup
        - self.reset                : Method
            Resetting method
        - self.updates              : Method
            Grab order data from firebase
        - self.update_orders_layout : Method
            Update layout in widget

        Returns
        -------
        None
        """
        if self.state != "down":
            self.set_pop_up()

        else:
            self.reset()
            self.update()
            self.update_orders_layout()
            self.manager.current = "OrderDoneScreen"
            self.manager.ids.order_done_screen.event()
            #self.manager.ids.submit_screen.order = self.order
            #self.manager.ids.submit_screen.additional_info = self.additional_info

    def close_popup(self, *args):
        """
        Method to close popup

        Parameters
        ----------
        - *args : list
            Stores any parameters

        Calls
        -----
        - self.popup.dismiss : Method
            Dismisses popup

        Returns
        -------
        None
        """
        self.popup.dismiss()

class ChefguiApp(App):

    def __init__(self):
        super().__init__()
        self.firebase = FIREBASE

    def build(self):
        pass

if __name__ == "__main__":
    a = ChefguiApp()
    a.run()
