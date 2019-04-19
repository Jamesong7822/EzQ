import RPi.GPIO as GPIO
import time

'''
connect black wire to ground
connect red middle wire to 5V
connect green wire to pin 11, GPIO 17

connect LED input to pin 36, GPIO16
'''

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(11, GPIO.IN)
GPIO.setup(3, GPIO.OUT)
GPIO.setup(36, GPIO.OUT)

while True:
    detection=GPIO.input(11)
    
    if detection==0:
        print('PIR sensor doesn\'t detect anyone, thus switch off the lights')
        GPIO.output(36, False)   #switch off the lights
        time.sleep(1)            #check again after 1 sec
    elif detection==1:
        print('PIR sensor detects someone, thus switch on the lights')
        GPIO.output(36, True)    #switch on the lights
        time.sleep(10)           #leave the lights on for 10secs to key in number
