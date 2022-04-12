import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import cv2
import numpy as np
import time
from datetime import date
today = date.today()
from datetime import datetime
now = datetime.now()


broker = "mqtt.eclipseprojects.io"
port = 1883
timelive=60


def save_image():

    image_name = str(now)+ str(".jpg")
    #cv2.VideoCapture(0) this can be 0, 1, 2 depending on your device id
    videoCaptureObject = cv2.VideoCapture(0)
    ret, frame = videoCaptureObject.read()
    cv2.imwrite(image_name, frame)
    videoCaptureObject.release()


    process_image()

def process_image():
    boxes = []
    confs = []
    class_ids = []


    image_name = str(now)+ str(".jpg")

    #loading the YoloV3 weights and configuration file using the open-cv dnn module
    net = cv2.dnn.readNet("yolov3.weights", "yolov3.cfg")

    #storing all the trained object names from the coco.names file in the list names[]
    names = []
    with open("coco.names", "r") as n:
        names = [line.strip() for line in n.readlines()]

    #running a foward pass by passing the names of layers of the output to be computed by net.getUnconnectedOutLayersNames()
    output_layers = [layer_name for layer_name in net.getUnconnectedOutLayersNames()]
    colors = np.random.uniform(0, 255, size=(len(names), 3))

    #reading  the image from the image_name variable (Same image which was saved by the save_image function)
    image = cv2.imread(image_name)
    height, width, channels = image.shape

    #using blobFromImage function to preprocess the data
    blob = cv2.dnn.blobFromImage(image, scalefactor=0.00392, size=(160, 160), mean=(0, 0, 0))
    net.setInput(blob)

    #getting X/Y cordinates of the object detected, scores for all the classes of objects in coco.names where the predicted object is class with the highest score, height/width of bounding box
    outputs = net.forward(output_layers)
    for output in outputs:
        for check in output:
            #this list scores stores confidence for each corresponding object
            scores = check[5:]

            #np.argmax() gets the class index with highest score which will help us get the name of the class for the index from the names list
            class_id = np.argmax(scores)
            conf = scores[class_id]
            #predicting with a confidence value of more than 40%
            if conf > 0.4:
                center_x = int(check[0] * width)
                center_y = int(check[1] * height)
                w = int(check[2] * width)
                h = int(check[3] * height)
                x = int(center_x - w / 2)
                y = int(center_y - h / 2)
                boxes.append([x, y, w, h])
                confs.append(float(conf))
                class_ids.append(class_id)

    #drawing bounding boxes and adding labels while removing duplicate detection for same object using non-maxima suppression
    indexes = cv2.dnn.NMSBoxes(boxes, confs, 0.5, 0.5)
    font = cv2.FONT_HERSHEY_PLAIN
    for i in range(len(boxes)):
        if i in indexes:
            x, y, w, h = boxes[i]
            label = str(names[class_ids[i]])
            color = colors[i]
            cv2.rectangle(image, (x, y), (x + w, y + h), color, 2)
            cv2.putText(image, label, (x, y - 5), font, 1, color, 1)

    #resizing and saving the the image
    width = int(image.shape[1] * 220 / 100)
    height = int(image.shape[0] * 220 / 100)
    dim = (width, height)
    resized = cv2.resize(image, dim, interpolation=cv2.INTER_AREA)
    
    cv2.imwrite('processed.jpg', resized)

    clock = datetime.now()


    cv2.imwrite("./Image-transfer-MQTT/" +str(clock) +str(".jpg"),resized)
    
    #reading the image and converting it to bytearray
    f = open("processed.jpg", "rb")
    fileContent = f.read()
    byteArr = bytes(fileContent)

    #topic to publish for our MQTT
    TOPIC = "IMAGE"
    client = mqtt.Client()

    #connecting to the MQTT broker
    client.connect(broker, port, timelive)

    #publishing the message with bytearr as the payload and IMAGE as topic
    publish.single(TOPIC, byteArr, hostname=broker)
    print("Published")

while True:
    save_image()
    time.sleep(5)


