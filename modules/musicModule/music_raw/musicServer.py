import threading
import queue
import json
import music_code as play
from httpserver import HTTP_Sever
from time import sleep
from flask import Flask, Response, abort, request

httpServerhandler = HTTP_Sever("ai_module_extension_server",hostAdddress = '0.0.0.0',portAddress="6000",debugFlag = False)

message_queue = queue.Queue()
plantSignal = 0
samplerate = 44100 
plantstr = ""
plantdataDict = ""
plantMusic = 0


def musicMain(name):
    pass
    print("Thread %s: starting", name)
    while True:

        if message_queue.empty():
            # log.info("Queue is empty")
            sleep(0.1)
            continue
        incoming_message_string = message_queue.get()

        plantdataDict = json.loads(incoming_message_string)
        plantMusic = int(plantdataDict["plantSignal"])
        play.musicPlay(plantMusic)


def musicUpdate():
    pass
    header = {"Content-Type": "application/txt"}
    try:
            '''
            fetch the data from network over http request. this function pass in endpoint
            '''
            data = request.get_data(cache=False)
            print("Message received:{}".format(data))
            data=data.decode('utf-8')
            message_queue.put(data)
            return 'valid message',header,204

    except Exception as msg:
            print('app','Exception:musicUpdate:{}'.format(msg))    
            return 'invalid message',header,400
    

def setupHttpServer(name):
    pass
    httpServerhandler.add_endpoint(rule='/update', endpoint='ai_module_extension', handler=musicUpdate, method=['POST'])
    print('app','HTTP server start running at 0.0.0.0:6000')
    httpServerhandler.run()






if __name__ == "__main__":
    
    print("|Welcome to plant-music code|")

    print("Main    : creating Server-thread")
    serverThreadHandle = threading.Thread(target=setupHttpServer, args=(1,))

    print("Main    : creating musicclient-thread")
    musicThreadHandle = threading.Thread(target=musicMain, args=(1,))

    print("Main    : start Server thread")
    serverThreadHandle.start()

    print("Main    : start music thread")
    musicThreadHandle.start()

    print("Main    : wait for the both thread to finish")
    serverThreadHandle.join()
    musicThreadHandle.join()

    print("Main    : Exiting from main application, Thank You !")