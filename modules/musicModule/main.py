# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for
# full license information.

import asyncio
import sys
import signal
import threading
from azure.iot.device.aio import IoTHubModuleClient
from scipy.io.wavfile import write
import numpy as np
import pygame
# from pygame import mixer
import json
import queue
from time import sleep
import requests


plantSignal = 0
samplerate = 44100 
base_music = "/app/twinkle-twinkle.wav"
plantstr = ""
plantdataDict = ""
plantMusic = 0
message_queue = queue.Queue()

# def get_piano_notes():
#     '''
#     Returns a dict object for all the piano 
#     note's frequencies
#     '''
#     try:
#         # White keys are in Uppercase and black keys (sharps) are in lowercase
#         octave = ['C', 'c', 'D', 'd', 'E', 'F', 'f', 'G', 'g', 'A', 'a', 'B'] 
#         # base_freq = 261.63 #Frequency of Note C4
#         #Frequency of Note C4
#         global base_freq
#         note_freqs = {octave[i]: base_freq * pow(2,(i/12)) for i in range(len(octave))}       
#         note_freqs[''] = 0.0
#         return note_freqs
#     except Exception as e:
#         print("Exception in get_piano_notes() : ",e)
    
# def get_wave(freq, duration=0.3):
#     try:
#         music_amplitude = 4096
#         t = np.linspace(0, duration, int(samplerate * duration))
#         wave = music_amplitude * np.sin(2 * np.pi * freq * t)
        
#         return wave
#     except Exception as e:
#         print("Exception in get_wave() : ",e)

        
# def get_song_data(music_notes):
#     try:
#         note_freqs = get_piano_notes()
#         song = [get_wave(note_freqs[note]) for note in music_notes.split('-')]
#         song = np.concatenate(song)
#         return song.astype(np.int16)
#     except Exception as e:
#         print("Exception in get_song_data() : ",e)
    

# def music():
#     try:
#         #Notes of "twinkle twinkle little star"
#         music_notes = 'C-C-G-G-A-A-G--F-F-E-E-D-D-C'
        
#         # next line create song object (Music file)
#         data = get_song_data(music_notes)
#         data = data * (16300/np.max(data))
#         write(base_music, samplerate, data.astype(np.int16))
#         print("no error")
        
#         pygame.init()
#         pygame.mixer.init()
#         pygame.mixer.music.load(base_music)
#         pygame.mixer.music.play()
#         while pygame.mixer.music.get_busy() == True:
#             continue
#         pygame.quit()
#     except Exception as e:
#         print("Exception in music() : ",e)

# def musicPlay(amplitude):    
#       print("Plant signal data: ", amplitude)
#       global base_freq
#       base_freq = amplitude /10  
#       # the above value we can vary after checking which amplitude needs which note and equate accordingly
      
#       # print("Base freq: " ,base_freq)
#       music()


# Event indicating client stop
stop_event = threading.Event()


def create_client():
    client = IoTHubModuleClient.create_from_edge_environment()

    # Define function for handling received messages
    async def receive_message_handler(message):
        # NOTE: This function only handles messages sent to "input1".
        # Messages sent to other inputs, or to the default, will be discarded
        if message.input_name == "input4":
            print("the data in the message received on input1 was ")
            print(message.data)

            #convert byte array into string then convert json string into dictionary
            plantstr = message.data.decode('utf-8')
            message_queue.put(plantstr)
            
            #TODO music code here

            print("forwarding message to output4")
            await client.send_message_to_output(message, "output4")

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

        if message_queue.empty():
            # log.info("Queue is empty")
            sleep(0.1)
            continue
        incoming_message_string = message_queue.get()
        plantdataDict = json.loads(incoming_message_string)

        print("Sending Plant info http Server running localhost:6000 :{}".format(plantdataDict))
        
        post_response = requests.post("http://0.0.0.0:6000/update", headers={"Content-Type": "application/json"}, data=incoming_message_string)
        print("response http request:{}".format(post_response))



def main():
   
    # if not sys.version >= "3.5.3":
    if not sys.version >= "3.11.2":
      raise Exception( "The sample requires python 3.5.3+. Current version of Python: %s" % sys.version )
    
    print( "IoT Hub Client for Python" )

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