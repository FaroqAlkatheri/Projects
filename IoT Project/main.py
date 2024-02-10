import socket
import machine
import time
import json
import network
import neopixel

#Configure Network Connection
ssid = 'TP-LINK_Extender_2.4GHz'
password = 'adel1234'
def connect_to_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)  # Create a station interface
    wlan.active(True)  # Activate the interface
    if not wlan.isconnected():  # Check if already connected
        print('Connecting to network...')
        wlan.connect(ssid, password)  # Connect to the network
        while not wlan.isconnected():  # Wait until connected
            pass
    print('Network config:', wlan.ifconfig())  # Display the network configuration

# Attempt to connect to Wi-Fi
connect_to_wifi(ssid, password)


# Create a NeoPixel object
np = neopixel.NeoPixel(machine.Pin(48), 1)


# potentiometer Pin setup Connected on Pin 5
potentiometer = machine.ADC(machine.Pin(5))
potentiometer.width(machine.ADC.WIDTH_12BIT)
# Adjust the attenuation if necessary. This setting is for input voltages up to approximately 3.6V
potentiometer.atten(machine.ADC.ATTN_11DB)


# photoresistor Pin setup Connected on Pin 4
photoresistor = machine.ADC(machine.Pin(4))
photoresistor.width(machine.ADC.WIDTH_12BIT)
photoresistor.atten(machine.ADC.ATTN_11DB)  # Suitable for input voltages up to approximately 3.6V

#socket init
HOST ='192.168.100.52'
PORT = 4400
BUF_SIZE = 1024
s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.connect((HOST,PORT))

#define a read sensors function
def readSensors():
    photoresistorValue = photoresistor.read()
    potentiometerValue = potentiometer.read()
    return photoresistorValue, potentiometerValue

#Incode data in JSON Format
def jsonData(photo, poten):
    data = {
        "photo": photo,
        "poten": poten
    }
    return json.dumps(data)


def sendTCP(json_data):
    s.sendall(json_data.encode('utf-8'))
    response = s.recv(1024)
    json_rcv = json.loads(response.decode('utf-8'))
    state = json_rcv['state']
    return state

def lightControl(state, poten):
    white_color = (255,255,255)
    no_color = (0,0,0)
    if state == 'on':
        color = white_color
    elif state == 'off':
        color = no_color
    
    if poten > 3000:
        delay = 2
    elif poten > 2000:
        delay = 1.5
    elif poten > 1000:
        delay = 1
    else:
        delay = 0.5

    np[0] = color
    np.write()
    time.sleep(delay)
    np[0] = no_color
    np.write()
    time.sleep(delay)    


while True:
    photo, poten = readSensors()  # Read the value from the photoresistor
    print(f"photo sensor value = {photo}\nPotentiometer value = {poten}")
    jsonMsg = jsonData(photo, poten)
    state = sendTCP(jsonMsg)
    print(f"State = {state}")
    lightControl(state, poten)
    time.sleep(0.5)
