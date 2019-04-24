import RPi.GPIO as GPIO
import time

'''
for PIR,
connect black wire to ground
connect red middle wire to 5V
connect green wire to pin 11, GPIO 17

connect LED input to pins in gpio_list
'''

gpio_list=[29, 31, 33, 35, 36, 37]
pir_pin=11

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(pir_pin, GPIO.IN)  #set up pir pin to get input

for led in gpio_list:
    GPIO.setup(led, GPIO.OUT)  #set up all the led pins as output

def on_all_lights():
    for led in gpio_list:
        GPIO.output(led, True)    #switch on the lights
    time.sleep(10)           #leave the lights on for 10secs for customer to key in number
       
def off_all_lights():
    for led in gpio_list:
        GPIO.output(led, False)   #switch off the lights
    time.sleep(1)            #check again after 1 sec

while True:
    detection=GPIO.input(pir_pin)
    if detection==0:
        print('PIR sensor doesn\'t detect anyone, thus switch off the lights')
        off_all_lights()
    elif detection==1:
        print('PIR sensor detects someone, thus switch on the lights')
        on_all_lights()




