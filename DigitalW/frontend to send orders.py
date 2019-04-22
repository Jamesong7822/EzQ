from firebase import Firebase

firebaseInstance = Firebase()
firebaseInstance.connect()

#------------------------CONSTANTS--------------------------------
store_name = 'Western Food'
#-----------------------------------------------------------------
new_food = 'spaghetti chicken chop'
addit_info = 'No spaghett'

#get the current order ids
order_data = firebaseInstance.get_data("orders")
store_order_data = order_data[store_name]
#used ids
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
new_order_dict['food'] = new_food
new_order_dict['ready'] = False
new_order_dict['addit_info'] = addit_info
new_order_dict['time_waited'] = 0
print('adding new id ' + str(new_id) + ' and data ' + str(new_order_dict))
firebaseInstance.db.child('orders').child(store_name).update({new_id:new_order_dict})

    

#from libdw import pyrebase
#
#url = "https://dw-1d-23b1f.firebaseio.com/"
#apikey = "AIzaSyA-UsBLa0RCdeCkopX2G_Zk8ztmIh7GZFM"
#
#config = {
#    "apiKey": apikey,
#    "databaseURL": url,
#}
#
#firebase = pyrebase.initialize_app(config)
#db = firebase.database()
#
#
#order_list=[]                              #initialize an empty order list
#
#
#while True:
#    db.child("order").set(order_list)
#    order = db.child("order").get()
#    
#    new_order=int(input('What is the new order?')) #get the new order
#    order = db.child("order").get()
#    
#    if order.val()==None:
#        pass                                  #if no order, dont retrieve anything
#    else:    
#        order_list=sorted(order.val())             #else, get the current order list
#    
#    order_list.append(new_order)               #add new order into the list  
#    order_list=sorted(order_list)
#    db.child("order").set(order_list)  #upload the new sorted order list to firebase
#    
#    
#
#
#
#'''
#
#order = db.child("order").get()
#print(order.key())
#print(order.val())
## to create a new node with our own key
#db.child("pie").set(3.14)
## to update existing entry
#db.child("pie").set(3.1415)
#db.child("love_dw").set(True)
#'''