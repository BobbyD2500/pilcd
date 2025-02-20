''' PiLCD '''

import paho.mqtt.client as mqttClient
import time
#import json
import ssl
from luma.core.interface.serial import spi, noop
from luma.core.render import canvas
from luma.core.virtual import sevensegment
from luma.led_matrix.device import max7219
import re
import os

'''
global variables
'''

connected = False  # Stores the connection status
secure = os.getenv('MQTT_SECURE', 'False').lower() == 'true'
BROKER_ENDPOINT = os.getenv('MQTT_HOST',"127.0.0.1")
PORT = int(os.getenv('MQTT_PORT',1883))
MQTT_USERNAME = os.getenv('MQTT_USERNAME')
MQTT_PASSWORD = os.getenv('MQTT_PASSWORD')
TLS_CERT_PATH = "/etc/ssl/certs/ca-certificates.crt"  # Put here the path of your TLS cert. Only required if secure is True
MQTT_PREFIX = os.getenv('MQTT_PREFIX',"pilcd")
LEFT_TOPIC = MQTT_PREFIX + "/left"
RIGHT_TOPIC = MQTT_PREFIX + "/right"
ALL_TOPIC = MQTT_PREFIX + "/all"
debug = os.getenv('DEBUG', 'False').lower() == 'true'
SPI_DEVICE = int(os.getenv('SPI_DEVICE',0))
SPI_PORT = int(os.getenv('SPI_PORT',0))
serial = spi(port=SPI_PORT, device=SPI_DEVICE, gpio=noop())
device = max7219(serial)
seg = sevensegment(device)
left="    "
right="    "

'''
Functions to process incoming and outgoing streaming
'''

def on_connect(client, userdata, flags, rc):
    global connected  # Use global variable
    if rc == 0:
        print("[INFO] Connected to broker")
        connected = True  # Signal connection
    else:
        print("[INFO] Error, connection failed")


def on_publish(client, userdata, result):
    if debug:
        print("Published!")


def connect(mqtt_client, mqtt_username, mqtt_password, broker_endpoint, port):
    global connected

    if not mqtt_client.is_connected():
        mqtt_client.username_pw_set(mqtt_username, password=mqtt_password)
        mqtt_client.on_connect = on_connect
        mqtt_client.on_publish = on_publish
        if secure:
            mqtt_client.tls_set(ca_certs=TLS_CERT_PATH, certfile=None,
                            keyfile=None, cert_reqs=ssl.CERT_REQUIRED,
                            tls_version=ssl.PROTOCOL_TLSv1_2, ciphers=None)
            mqtt_client.tls_insecure_set(False)
        mqtt_client.connect(broker_endpoint, port=port)
        mqtt_client.loop_start()
        mqtt_client.subscribe([(LEFT_TOPIC,0),(RIGHT_TOPIC,0), (ALL_TOPIC,0)])
        mqtt_client.message_callback_add(LEFT_TOPIC,left_command)
        mqtt_client.message_callback_add(RIGHT_TOPIC,right_command)
        mqtt_client.message_callback_add(ALL_TOPIC,all_command)
        attempts = 0

        while not connected and attempts < 5:  # Wait for connection
            #print(connected)
            print("Attempting to connect...")
            time.sleep(1)
            attempts += 1

    if not connected:
        print("[ERROR] Could not connect to broker")
        return False

    return True


def publish(mqtt_client, topic, payload):

    try:
        mqtt_client.publish(topic, payload)

    except Exception as e:
        print("[ERROR] Could not publish data, error: {}".format(e))

def left_command(client, userdata, message):
    global left,right
    if debug:
        print("Received Command: "+str(message.payload)+" of type "+str(type(message.payload)))
    text = message.payload.decode("utf-8")
    text = convert_time(text)
    if(len(text)-len(re.findall('\w\.',text))<=4):
        left = text.ljust(4+len(re.findall('\w\.',text)))
        seg.text=left+right

def right_command(client, userdata, message):
    global left,right
    if debug:
        print("Received Command: "+str(message.payload)+" of type "+str(type(message.payload)))
    text = message.payload.decode("utf-8")
    text = convert_time(text)
    if(len(text)-len(re.findall('\w\.',text))<=4):
        right = text.rjust(4+len(re.findall('\w\.',text)))
        seg.text=left+right

def all_command(client, userdata, message):
    global left, right
    if debug:
        print("Received Command: "+str(message.payload)+" of type "+str(type(message.payload)))
    text = message.payload.decode("utf-8")
    text = convert_time(text)
    if(len(text)-len(re.findall('\w\.',text))<=8):
        seg.text=text
        left="    "
        right="    "

def convert_time(text):
    newtext=re.sub('0?(1\d|\d):(\d{2}).*','\\1.\\2',text)
    return newtext

if __name__ == '__main__':
    if(MQTT_USERNAME == None or MQTT_PASSWORD == None):
        print("[ERROR] Credentials not provided. Ensure MQTT_USERNAME and MQTT_PASSWORD environmental variables are set")
        exit(1)
#Create class and send state immediately
    mqtt_client = mqttClient.Client(mqttClient.CallbackAPIVersion.VERSION1)
    connect(mqtt_client, MQTT_USERNAME, MQTT_PASSWORD, BROKER_ENDPOINT, PORT)
    while True:
        connect(mqtt_client, MQTT_USERNAME, MQTT_PASSWORD, BROKER_ENDPOINT, PORT)
        time.sleep(0.1)
