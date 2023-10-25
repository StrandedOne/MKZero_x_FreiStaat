from gpiozero import LED
import time
import datetime
import os

import serial
serialPort=serial.Serial(port="/dev/ttyACM0",baudrate=9600,bytesize=8, timeout=2, stopbits=serial.STOPBITS_ONE)
ZeroTrigger = LED(17)
Relay = LED(22)
datum=datetime.datetime.now()
Zeit=(datum.strftime("%X"))
datum=datetime.date.today()

newpath = r'/home/pi/Desktop/%s' %datum
if not os.path.exists(newpath):
	os.makedirs(newpath)
	
header="Voltage in mV \t time in ms \n"
with open('{}/{}.txt' .format(newpath,Zeit),'w') as f:
	f.write(header)


Relay.off() # Relay.on() --> binds WE to WE
ZeroTrigger.on() # ZeroTrigger.off() --> Begins recording with MKRZERO 
time.sleep(1)
ZeroTrigger.off() # ZeroTrigger.off() --> Begins recording with MKRZERO 
i=0

while(i<1000):
	
	time.sleep(0.25)
	#print("stop")
	while(serialPort.in_waiting > 0):
		#serialPort.write(bytes(52))
		MKB=serialPort.inWaiting()
		serialString=serialPort.read(MKB)
		value=serialString.decode('Ascii')
		value=value.split(',')
		Potential=value[0]
		Time=value[1]
		with open('{}/{}.txt' .format(newpath,Zeit),'a') as f:
			f.write(Potential+ '\t'+',\t' + Time)
		print(value)
	
		#time.sleep(0.5)
	i=i+1
	
	#print('stop2')
ZeroTrigger.off()
