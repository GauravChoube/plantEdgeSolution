# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for
# full license information.

import asyncio
import sys
import signal
import threading
from azure.iot.device.aio import IoTHubModuleClient
import json
import time

import pandas as pd
import pickle
from sklearn.preprocessing import StandardScaler

plantMessage={}
plantMessageJson=None
pickled_model=None

# Event indicating client stop
stop_event = threading.Event()

def aiInferencing(data):
    #Take input data , load into ai module , predict behavior and append to current message 
    # send as json
    global pickled_model

    t1=round(time.time()*1000)

    plantMessage = json.loads(data)
    #print("cp1")
    plantDataList = [plantMessage["temperature"],plantMessage["humidity"],plantMessage["plantSignal"],plantMessage["luminosity"]]
    print("plantDataList:",plantDataList)

    #TODO Add prediction code here
    
    # print("cp2")
    pickled_model = pickle.load(open('mlp_temp_alpha.pkl', 'rb')) #convert the list to a DataFrame
    # print("cp3")
    raw_df = pd.DataFrame(data = plantDataList).T
    # print("cp4")
    standard_pkl_fitter = pickle.load(open('scaled_X_train.pkl', 'rb')) # scale the test data before giving it as an input to the model
    # print("cp5")
    scaled_test_new = pd.DataFrame(standard_pkl_fitter.transform(raw_df))
    # print("cp6")
    pred_outcome = pickled_model.predict(scaled_test_new)
    # print("cp7")

    plantMessage["plantMood"] = pred_outcome[0]
    # print("plantMood------- ", plantMessage["plantMood"])
    plantMessage["time"] = time.time()
    # print("Time ------", plantMessage["time"])

    t2=round(time.time()*1000)

    print("[{}]mood detected with inferencing time:{}ms".format(plantMessage["plantMood"],t2-t1))
    return json.dumps(plantMessage)

def create_client():
    client = IoTHubModuleClient.create_from_edge_environment()

    # Define function for handling received messages
    async def receive_message_handler(message):
        # NOTE: This function only handles messages sent to "input1".
        # Messages sent to other inputs, or to the default, will be discarded

        # wait for incoming message on input1
        if message.input_name == "input1":
            print("the data in the message received on input1 was ")
            print(message.data)
            plantMessage = message.data.decode('utf-8')
            print(plantMessage)

            # process and do ai computing
            plantMessageJson=aiInferencing(plantMessage)
            
            #send to iot module on output2
            print("forwarding mesage to output2:",plantMessageJson)
            await client.send_message_to_output(plantMessageJson, "output2")

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
        await asyncio.sleep(5000)
        
def main():
    if not sys.version >= "3.5.3":
        raise Exception( "The sample requires python 3.5.3+. Current version of Python: %s" % sys.version )
    print ( "IoT Hub Client for Python" )

    global pickled_model

    # pickled_model = pickle.load(open('model.pkl', 'rb')) #import the pickled model

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
