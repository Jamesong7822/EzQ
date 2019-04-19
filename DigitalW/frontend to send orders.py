from libdw import pyrebase

url = "https://dw-1d-23b1f.firebaseio.com/"
apikey = "AIzaSyA-UsBLa0RCdeCkopX2G_Zk8ztmIh7GZFM"

config = {
    "apiKey": apikey,
    "databaseURL": url,
}

firebase = pyrebase.initialize_app(config)
db = firebase.database()


order_list=[]                              #initialize an empty order list


while True:
    db.child("order").set(order_list)
    order = db.child("order").get()
    
    new_order=int(input('What is the new order?')) #get the new order
    order = db.child("order").get()
    
    if order.val()==None:
        pass                                  #if no order, dont retrieve anything
    else:    
        order_list=sorted(order.val())             #else, get the current order list
    
    order_list.append(new_order)               #add new order into the list  
    order_list=sorted(order_list)
    db.child("order").set(order_list)  #upload the new sorted order list to firebase
    
    



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