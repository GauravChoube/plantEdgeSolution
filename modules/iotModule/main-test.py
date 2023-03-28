# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for
# full license information.
import time
import json
import asyncio
import sys
import signal
import threading
from azure.iot.device.aio import IoTHubModuleClient

# count = 0
# newcount = 0
# /////////////////////////////
# plantsignal = 0
plantdataDict = []
# deviation = 50
# count = 0
# plantOld=0
plantstr=''
# /////////////////////////////
# Event indicating client stop
stop_event = threading.Event()

counter_flag = False

# plantOld=''

def create_client():
    client = IoTHubModuleClient.create_from_edge_environment()
    print("inside functn")
    plantOld = ''
    plantNew = ''

    # Define function for handling received messages
    async def receive_message_handler(message):
            
        # NOTE: This function only handles messages sent to "input1".
        # Messages sent to other inputs, or to the default, will be discarded
        if message.input_name == "input2":
            print("the data in the message received on input1 was ")
            
            # plantOld =+ plantNew
            # for the first time
            print(message.data)
            #convert byte array into string then convert json string into dictionary
            plantstr = message.data.decode('utf-8')
            plantdataDict = json.loads(plantstr)
            print("plantdict")
            print(plantdataDict)
            #taking plantsignal value from this dictionary
            print(plantOld)
            print("before if")
            plantNew=plantdataDict["plantMood"]
            
            if plantNew == plantOld:
                #do my operaton sendig
                print("if condn")
                pass
                message["time"] = time.time()
                await client.send_message_to_output(message, "output3")
                print("msg sent")
                plantOld=plantNew
            
            print(plantOld)
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
        await asyncio.sleep(1000)


def main():
    # if not sys.version >= "3.5.3":
        # raise Exception( "The sample requires python 3.5.3+. Current version of Python: %s" % sys.version )
    print ( "IoT Hub Client for Python" )
    # plantOld=0

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