from libdw import pyrebase
#from firebase import firebase

url = "https://dw-1d-23b1f.firebaseio.com/"
apikey = "AIzaSyA-UsBLa0RCdeCkopX2G_Zk8ztmIh7GZFM"

config = {
    "apiKey": apikey,
    "databaseURL": url,
}

firebase = pyrebase.initialize_app(config)
db = firebase.database()


while True:    
    order = db.child("order").get()
    if order.val()==None:
        pass
    else:
        order_list=sorted(order.val())
        print(order_list)                  #show the chef the order list which is sorted so he can cook the dish with most orders first

   

    current_dish=int(input('What did you just cook?'))   #know the current dish thats cooked
    order = db.child("order").get()
    if order.val()==None:
        pass
    else:
        order_list=sorted(order.val())                      #get updated order list again as there will be a time lag above
        if current_dish in order_list:
            order_list.remove(current_dish)                 #remove the current dish from the order list
        else:
            pass
        order_list=sorted(order_list)
        db.child("order").set(order_list)               #reupload the new order list

            
    




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