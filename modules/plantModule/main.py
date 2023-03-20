# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for
# full license information.

import asyncio
import sys
import signal
import threading
from azure.iot.device.aio import IoTHubModuleClient
import json
import random

# Pi Dependencies
from time import time, sleep, strftime
import board
import busio
import adafruit_dht
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

dhtDevice = adafruit_dht.DHT22(board.D4)
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)

plant = AnalogIn(ads, ADS.P1)
ldr = AnalogIn(ads, ADS.P3)

# Event indicating client stop
stop_event = threading.Event()

plantMessage={}
plantMessageJson=None

def getPlantData():
    # capture the all data from sensor 
    # put into dictionary

    try:
        plant_val = 0
        ldr_val = 0
        temperature = dhtDevice.temperature
        humidity = dhtDevice.humidity
        for i in range (0, 50):
            plant_val = plant.value + plant_val
            ldr_val = ldr.value + ldr_val 
        
        plant_val = plant_val/50
        ldr_val = ldr_val/50
        
        #{"plantSignal": 1129,"temperature": 20.0,"humidity": 60,"luminosity": 778,"plantMood": Normal}
        plantMessage["plantSignal"] = plant_val
        plantMessage["temperature"] = temperature
        plantMessage["humidity"] = humidity
        plantMessage["luminosity"] = ldr_val
        
        #return in json formate
        return json.dumps(plantMessage)

    except RuntimeError as error:
        return None

def create_client():
    client = IoTHubModuleClient.create_from_edge_environment()

    # Define function for handling received messages
    async def receive_message_handler(message):
        # NOTE: This function only handles messages sent to "input1".
        # Messages sent to other inputs, or to the default, will be discarded
        if message.input_name == "input1":
            print("the data in the message received on input1 was ")
            print(message.data)
            # print("custom properties are")
            # print(message.custom_properties)
            # print("forwarding mesage to output1")
            # await client.send_message_to_output(message, "output1")

    try:
        # Set handler on the client
        client.on_message_received = receive_message_handler
    except:
        # Cleanup if failure occurs
        client.shutdown()
        raise

    return client

async def run_sample(client):
    # Customize this coroutine to do whatever tasks the module initiates
    # e.g. sending messages
    while True:
        plantMessageJson=getPlantData()
        if plantMessageJson is not None:
            print("data in the message created on input1: ",plantMessageJson)
            await client.send_message_to_output(plantMessageJson, "output1")
        await asyncio.sleep(5)

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
