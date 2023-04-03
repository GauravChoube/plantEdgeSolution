#----------for pin configuration--------------
#pinout

import bluetooth
import RPi.GPIO as GPIO 		#Importing the GPIO library to use the GPIO pins of Raspberry pi
import os

os.system('hciconfig hci0 piscan')

host = ""

light_pin=17
fan_pin=27
heat_pin=22

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


try:
		server_socket.bind((host,port))
		print("Bluetooth Binding Completed")
except:
		print("Bluetooth Binding Failed")
	
server_socket.listen(2)

#get port number of server socket
port = server_socket.getsockname()[1]
print('listening on port ',port)

#-------------------------UUID must be same on the app side----------------------------------------------
uuid='00001101-0000-1000-8000-00805F9B34FB'

bluetooth.advertise_service(server_socket,
			   'RPi',
			   service_id=uuid,
			   )
#--------------------------------------------------------------------------------------------------------
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
#--------------------------------------------------------------------------------------------------------
# Receiving data and controlling GPIO pins

while True: 
	
	print('----------------------------------------------------')
	print('Waiting for connection on RFCOMM channel %d' % port)
	client_socket = None
	try: 
		# Server accepts the clients request and assigns a mac address, accepts incoming bluetooth connection.
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
	       if not 'data':
	        break
	      #---------------------- on and off ------------------------
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
		pass
		
	except KeyboardInterrupt:
		break
		
	except:
		# Making all the output pins LOW
		print()
		print('disconnected...')
		GPIO.cleanup()
		# Closing the client and server connection
		client_socket.close()
		server_socket.close()
		print('Done, socket closed')
		break
