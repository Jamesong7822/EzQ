#from libdw import pyrebase
##from firebase import firebase
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

from firebase import Firebase

firebaseInstance = Firebase()
firebaseInstance.connect()

#------------------------CONSTANTS--------------------------------
store_name = 'Western Food'
#-----------------------------------------------------------------

while True:
    food_to_make = []
    food_is_ready_id = []
    order_data = firebaseInstance.get_data("orders")
    store_order_data = order_data[store_name]
    for order_id,item in store_order_data.items():
        if item['ready'] == False:
            food_to_make.append(order_id + ' ' + item['food']+' '+item['addit_info']+' '+ str(item['time_waited']))
        else:
            food_is_ready_id.append(order_id)
    food_to_make = sorted(food_to_make)
    print(food_to_make)
    
    order_id=input('What id did you just cook?')
    if order_id in food_is_ready_id:
        print('That order id is already ready')
        continue
    
    try:
        order_data = firebaseInstance.get_data("orders")
        store_order_data = order_data[store_name]
        customer_id = store_order_data[order_id]['id']
        try:
            customer_data = firebaseInstance.get_data("customers")
            phone_num = customer_data[customer_id]['mobile']
            print('we will send a message to ' + phone_num + ' through twilio')
            firebaseInstance.db.child('orders').child('{}'.format(store_name)).child('{}'.format(order_id)).update({"ready":True})
        except:
            print('Error, the customer_id does not exist')
    except:
        print('Error, the order id specified does not exist')
#    if order.val()==None:
#        pass
#    else:
#        order_list=sorted(order.val())
#        print(order_list)                  #show the chef the order list which is sorted so he can cook the dish with most orders first
#
#   
#
#    current_dish=int(input('What did you just cook?'))   #know the current dish thats cooked
#    order = db.child("order").get()
#    if order.val()==None:
#        pass
#    else:
#        order_list=sorted(order.val())                      #get updated order list again as there will be a time lag above
#        if current_dish in order_list:
#            order_list.remove(current_dish)                 #remove the current dish from the order list
#        else:
#            pass
#        order_list=sorted(order_list)
#        db.child("order").set(order_list)               #reupload the new order list

            
    




'''
order = db.child("order").get()
print(order.key())
print(order.val())
# to create a new node with our own key
db.child("pie").set(3.14)
# to update existing entry
db.child("pie").set(3.1415)
db.child("love_dw").set(True)
'''