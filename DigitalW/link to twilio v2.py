from firebase import Firebase

firebaseInstance = Firebase()
firebaseInstance.connect()


#------------------------CONSTANTS--------------------------------
store_name = 'Western Food'
#-----------------------------------------------------------------


while True:  #infinite loop
    order_id=input('Please input the order number:')
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

    
    



    