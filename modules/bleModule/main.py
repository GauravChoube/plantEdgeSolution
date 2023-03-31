# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for
# full license information.

import asyncio
import sys
import signal
import threading
from azure.iot.device.aio import IoTHubModuleClient

import bluetooth
import RPi.GPIO as GPIO
import os

os.system('sudo hciconfig hci0 piscan')

host = ""

light_pin=22 #pin 15
fan_pin=23 #pin 16
heat_pin=24 #pin 18

GPIO.setmode(GPIO.BCM)     		#programming the GPIO by BCM pin numbers. (like PIN40 as GPIO21)

GPIO.setwarnings(False)

GPIO.setup(light_pin,GPIO.OUT)  #initialize GPIO17 (LED) as an output Pin
GPIO.setup(fan_pin,GPIO.OUT) 
GPIO.setup(heat_pin,GPIO.OUT) 

GPIO.output(light_pin,0)
GPIO.output(fan_pin,0)
GPIO.output(heat_pin,0)

port = 1    				# Raspberry Pi port for Bluetooth Communication

# Creating Socket(endpoint for Bluetooth RFCOMM communication
server_socket=bluetooth.BluetoothSocket( bluetooth.RFCOMM )
print('Bluetooth Socket Created')

# Declaring Action functions
def lighton():
    GPIO.output(light_pin, GPIO.HIGH)
    send_data = 'Light is On!'
    print('Light is on')

def lightoff():
    GPIO.output(light_pin, GPIO.LOW)
    send_data = 'Light is off!'
    print('Light is off')
#-----   
def fanon():
    GPIO.output(fan_pin, GPIO.HIGH)
    send_data = 'fan is On!'
    print('fan is on')

def fanoff():
    GPIO.output(fan_pin, GPIO.LOW)
    send_data = 'fan is off!'
    print('fan is off')
    #-----
def heaton():
    GPIO.output(heat_pin, GPIO.HIGH)
    send_data = 'heat is On!'
    print('heat is on')

def heatoff():
    GPIO.output(heat_pin, GPIO.LOW)
    send_data = 'heat is off!'
    print('heat is off')
#-----   
def invalid():
    GPIO.output(light_pin, GPIO.LOW)
    GPIO.output(fan_pin, GPIO.LOW)
    GPIO.output(heat_pin, GPIO.LOW)
    send_data = '\nInvalid Input\n'
    print('invalid input')


# Event indicating client stop
stop_event = threading.Event()


def create_client():
    client = IoTHubModuleClient.create_from_edge_environment()
    print('----------------------------------------------------')
    print('Waiting for connection on RFCOMM channel %d' % port)
    client_socket = None

    server_socket.listen(2)

    #get port number of server socket
    port = server_socket.getsockname()[1]
    print('listening on port ',port)

    #-------------------------UUID must be same on the app side----------------------------------------------
    uuid='00001101-0000-1000-8000-00805F9B34FB'
    bluetooth.advertise_service(server_socket, 'RPi', service_id=uuid)

    # Define function for handling received messages
    async def receive_message_handler(message):
        # NOTE: This function only handles messages sent to "input1".
        # Messages sent to other inputs, or to the default, will be discarded
        if message.input_name == "input1":
            print("the data in the message received on input1 was ")
            print(message.data)
            print("custom properties are")
            print(message.custom_properties)
            print("forwarding mesage to output1")
            await client.send_message_to_output(message, "output1")

    try:
        # Set handler on the client
        client.on_message_received = receive_message_handler
        server_socket.bind((host,port))
        print("Bluetooth Binding Completed")

        client_socket,client_address = server_socket.accept()
        print("Accepted connection from ",client_address)
        print("Client:", client_socket)
        data = client_socket.recv(1024).decode(encoding='utf8').rstrip() #msg can only be only 1024
        print()
        print("data received from android application: %s" % data)

        datas = data.split()
        print()
        print('individual data', datas)
        print()

        for dataX in datas:
    	      #---------------------- on and off ------------------------

            if not 'data':
                break

            elif 'lightON' in dataX:
                lighton()
            elif 'lightOFF' in dataX:
                lightoff()

            elif 'fanON' in dataX:
                fanon()
            elif 'fanOFF' in dataX:
                fanoff()

            elif 'heatON' in dataX:
                heaton()
            elif 'heatOFF' in dataX:
                heatoff()
                
            else:
                invalid()

    except IOError:
        exit
    
    except KeyboardInterrupt:
        exit

    except:
        # Cleanup if failure occurs
        print("Bluetooth Binding Failed")
        client.shutdown()

        print('disconnected...')
        GPIO.cleanup()
        # Closing the client and server connection
        client_socket.close()
        server_socket.close()
        print('Done, socket closed')
        raise

    return client


async def run_sample(client):
    # Customize this coroutine to do whatever tasks the module initiates
    # e.g. sending messages
    while True:
        await asyncio.sleep(1000)


def main():
    if not sys.version >= "3.5.3":
        raise Exception( "The sample requires python 3.5.3+. Current version of Python: %s" % sys.version )
    print ( "IoT Hub Client for Python" )

    # NOTE: Client is implicitly connected due to the handler being set on it
    client = create_client()

    # Define a handler to cleanup when module is is terminated by Edge
    def module_termination_handler(signal, frame):
        print ("IoTHubClient sample stopped by Edge")
        stop_event.set()

    # Set the Edge termination handler
    signal.signal(signal.SIGTERM, module_termination_handler)

    # Run the sample
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(run_sample(client))
    except Exception as e:
        print("Unexpected error %s " % e)
        raise
    finally:
        print("Shutting down IoT Hub Client...")
        loop.run_until_complete(client.shutdown())
        loop.close()


if __name__ == "__main__":
    main()
