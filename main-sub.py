
import paho.mqtt.client as mqtt
from datetime import date
today = date.today()
from datetime import datetime
now = datetime.now()

import cv2
import numpy as np


broker = "mqtt.eclipseprojects.io"
port = 1883
timelive = 60

image_name= str(str(now)+ str(".jpg"))

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    #subscribe to the topic IMAGE, this is the same topic which was used to published the image on the previous device
    client.subscribe("IMAGE")


def on_message(client, userdata, msg):

    image_name= str(str(now)+ str(".jpg"))
    #create/open jpg file [detected_objects.jpg] to write the received payload
    f = open(image_name, "wb")
    f.write(msg.payload)

    data = f.write(msg.payload)

    print(data)
    f.close()

def mqtt_sub():
    client = mqtt.Client()
    client.connect(broker, port, timelive)
    client.on_connect = on_connect
    client.on_message = on_message
    client.loop_forever()


while True:
    mqtt_sub()
    sleep(5)

