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
from pygame import mixer
import json

plantSignal = 0
samplerate = 44100 
base_music = "twinkle-twinkle.wav"
plantstr = ""
plantdataDict = ""
plantMusic = 0

def get_piano_notes():
    '''
    Returns a dict object for all the piano 
    note's frequencies
    '''
    # White keys are in Uppercase and black keys (sharps) are in lowercase
    octave = ['C', 'c', 'D', 'd', 'E', 'F', 'f', 'G', 'g', 'A', 'a', 'B'] 
    # base_freq = 261.63 #Frequency of Note C4
     #Frequency of Note C4
    global base_freq
    note_freqs = {octave[i]: base_freq * pow(2,(i/12)) for i in range(len(octave))}       
    note_freqs[''] = 0.0
    return note_freqs
    
def get_wave(freq, duration=0.3):
    music_amplitude = 4096
    t = np.linspace(0, duration, int(samplerate * duration))
    wave = music_amplitude * np.sin(2 * np.pi * freq * t)
    
    return wave
        
def get_song_data(music_notes):
    note_freqs = get_piano_notes()
    song = [get_wave(note_freqs[note]) for note in music_notes.split('-')]
    song = np.concatenate(song)
    return song.astype(np.int16)
    

def music():
    #Notes of "twinkle twinkle little star"
    music_notes = 'C-C-G-G-A-A-G--F-F-E-E-D-D-C'
    
    # next line create song object (Music file)
    data = get_song_data(music_notes)
    data = data * (16300/np.max(data))
    write(base_music, samplerate, data.astype(np.int16))

    pygame.init()
    pygame.mixer.init()
    pygame.mixer.music.load(base_music)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy() == True:
        continue
    pygame.quit()

def musicPlay(amplitude):    
      print("Plant signal data: ", amplitude)
      global base_freq
      base_freq = amplitude /10  
      # the above value we can vary after checking which amplitude needs which note and equate accordingly
      
      # print("Base freq: " ,base_freq)
      music()


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
            plantdataDict = json.loads(plantstr)
            plantMusic = int(plantdataDict["plantSignal"])
            musicPlay(plantMusic)


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
        await asyncio.sleep(1000)


def main():
#    if not sys.version >= "3.5.3":
#       raise Exception( "The sample requires python 3.5.3+. Current version of Python: %s" % sys.version )
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