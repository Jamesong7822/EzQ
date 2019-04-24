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
        super(Screen, self).__init__()
        self.order = StringProperty(None)
        self.state = StringProperty(None)
        self.additional_info = StringProperty(None)
        self.popup = None
        self.btns = []
        self.firebase = FIREBASE

        #Get the list of
        menu_list = ["Chicken Chop Spaghetti", "Grilled Fish Spaghetti", "C", "D", "E", "F"]
        for i in menu_list:
            btn = ToggleButton(text=i, group="menu")
            btn.bind(on_press = self.get_order)
            self.btns.append(btn)
            self.grid.add_widget(btn)

    def get_order(self, togglebutton):
        tb = togglebutton

        self.order = str(tb.text)
        self.state = str(tb.state)

    def get_additional_info(self):
        self.additional_info = str(self.ids.additional_info_input.text)

    def set_pop_up(self):
        content = self.popup_layout()
        if not self.popup:
            self.popup = Popup(title="Warning", content=content, auto_dismiss=True, size_hint=(0.5, 0.5))
        self.popup.open()

    def popup_layout(self):
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
        if self.state != "down":
            self.set_pop_up()

        else:
            self.reset()
            self.manager.current = "SubmitScreen"
            self.manager.ids.submit_screen.update_nums_layout()
            self.manager.ids.submit_screen.order = self.order
            self.manager.ids.submit_screen.additional_info = self.additional_info

    def submit_order(self):
        pass

    def reset(self):
        for i in self.btns:
            if i.state == "down":
                i.state = "normal"
        self.ids.additional_info_input.text = ""


class SubmitScreen(Screen):
    order = StringProperty()
    additional_info = StringProperty()

    def __init__(self, **kwargs):
        super(Screen, self).__init__()
        self.firebase = FIREBASE
        self.nums = None
        self.num = StringProperty(None)
        self.state = StringProperty(None)
        self.popup = None
        self.order_btns = []


    def get_nums(self):
        # Clear pre-existing widgets
        if self.order_btns:
            for x in self.order_btns:
                self.ids.boxy.remove_widget(x)

        # Get data from database
        data = self.firebase.get_data("customers")
        #print(data)

        # Get keys - order nums
        key = []
        for customer_id, customer in data.items():
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
        tb = togglebutton
        self.num = str(tb.text)
        self.state = str(tb.state)
        self.customer_id = tb.text.split(':')[0]

    def update_nums_layout(self):
        self.nums = self.get_nums()
        for num in self.nums:
            btn = ToggleButton(text=num, group="nums")
            btn.bind(on_press=self.bind_nums)
            self.order_btns.append(btn)
            self.ids.boxy.add_widget(btn)

    def set_pop_up(self):
        content = self.popup_layout()
        if not self.popup:
            self.popup = Popup(title="Warning", content=content, auto_dismiss=True, size_hint=(0.5, 0.5))
        self.popup.open()

    def popup_layout(self):
        layout = BoxLayout(orientation="vertical")
        text = Label(text="Please select a number")
        btn = Button(text="OKAY!")
        btn.bind(on_release=self.close_popup)
        layout.add_widget(text)
        layout.add_widget(btn)
        return layout

    def update(self):
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
        if self.state != "down":
            self.set_pop_up()

        else:
            self.update()
            self.manager.current = "MenuScreen"
            #self.manager.ids.submit_screen.order = self.order
            #self.manager.ids.submit_screen.additional_info = self.additional_info

    def close_popup(self, *args):
        self.popup.dismiss()
        
#This screen is just a buffer to update that it is done
class OrderDoneScreen(Screen):
    
    def __init__(self, **kwargs):
        #Init the parent class
        super(Screen, self).__init__()
#        self.manager.current = "OrderCompletionScreen"
#        self.go_back()
        
    def go_back(self):
#        sleep(1)
        self.manager.ids.order_completion_screen.update_orders_layout()
        self.manager.current = "OrderCompletionScreen"


class OrderCompletionScreen(Screen):
    order = StringProperty()
    additional_info = StringProperty()

    def __init__(self, **kwargs):
        print('INITING ORDER COMPLETION SCREEN')
        super(Screen, self).__init__()
        self.firebase = FIREBASE
        self.nums = None
        self.num = StringProperty(None)
        self.state = StringProperty(None)
        self.popup = None
        self.order_btns = []
        #Get the information from the internet
        self.update_orders_layout()


    def get_orders(self):
        print('GETTING NUMS')
        # Clear pre-existing widgets
       
#        if self.order_btns:
#            for x in self.order_btns:
#                self.ids.boxy.remove_widget(x)

        # Get order data from database
        data = self.firebase.get_data("orders")
        print(data)
        #Get particular data for store
        store_data = data[STORE_NAME]

        # Get keys - order nums
        #We only want the keys of those whose food ready is false
        key = []
        for order_id, order in store_data.items():
            if order['ready'] == False:
                key.append(order_id)
                print(order_id)
#        key = [x for x in data]

        # Sort the keys list
        sorted(key, reverse=True)

        # List all the uncompleted orders
        self.nums = []
        for k in key:
            d = store_data[k]
            self.nums.append(k + ':' + d['food'] + ' ' + d['addit_info'] + ' ' + str(d['time_waited']))
#        self.nums = [x["mobile"] for x in [data[y] for y in key[:3]]]

        return self.nums

    def bind_nums(self, togglebutton):
        tb = togglebutton
        self.num = str(tb.text)
        self.state = str(tb.state)
        self.selected_order_id = tb.text.split(':')[0]

    def update_orders_layout(self):
        self.nums = self.get_orders()
        self.ids.boxy.clear_widgets()
        for num in self.nums:
            btn = ToggleButton(text=num, group="nums")
            btn.bind(on_press=self.bind_nums)
            self.order_btns.append(btn)
            self.ids.boxy.add_widget(btn)
            print(self.order_btns)

    def set_pop_up(self):
        content = self.popup_layout()
        if not self.popup:
            self.popup = Popup(title="Warning", content=content, auto_dismiss=True, size_hint=(0.5, 0.5))
        self.popup.open()

    def popup_layout(self):
        layout = BoxLayout(orientation="vertical")
        text = Label(text="Please select a number")
        btn = Button(text="OKAY!")
        btn.bind(on_release=self.close_popup)
        layout.add_widget(text)
        layout.add_widget(btn)
        return layout

    def update(self):
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
        self.firebase.db.child('orders').child('{}'.format(STORE_NAME)).child('{}'.format(self.selected_order_id)).update({"ready":True})
        
#        # Used ids
#        used_ids = []
#        for order_id,item in store_order_data.items():
#            used_ids.append(order_id)
#        new_id = None
#        for i in range(1,999):
#            i = '{:0>3}'.format(str(i))
#            if i not in used_ids:
#                new_id = i
#                break
#        new_order_dict = {}
#        new_order_dict['food'] = self.order
#        new_order_dict['ready'] = False
#        new_order_dict['addit_info'] = self.additional_info
#        new_order_dict['time_waited'] = 0
#        new_order_dict['id'] = self.customer_id
#        new_order_dict["order_time"] = int(time.time())
#        print('adding new id ' + str(new_id) + ' and data ' + str(new_order_dict))
#        self.firebase.update(["orders", STORE_NAME], {new_id:new_order_dict})
#        #update that the customer is served
#        self.firebase.update(["customers",self.customer_id],{'served':True})
    def reset(self):
        for i in self.order_btns:
           self.ids.boxy.remove_widget(i)
        #self.ids.additional_info_input.text = ""

    def check_orders(self):
        if self.state != "down":
            self.set_pop_up()

        else:
            self.reset()
            self.update()
            self.update_orders_layout()
            self.manager.current = "OrderDoneScreen"
            #self.manager.ids.submit_screen.order = self.order
            #self.manager.ids.submit_screen.additional_info = self.additional_info

    def close_popup(self, *args):
        self.popup.dismiss()

class chefGUIApp(App):

    def __init__(self):
        super().__init__()
        self.firebase = FIREBASE

    def build(self):
        pass

if __name__ == "__main__":
    a = chefGUIApp()
    a.run()
