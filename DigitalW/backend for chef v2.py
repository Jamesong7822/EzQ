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
