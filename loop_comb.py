from gpiozero import LED
import sys
sys.path.append('/home/pi/FreiStat-Framework/Python')  #adds dependencies
sys.path.append('/usr/lib/python3/dist-packages')
sys.path.append('/home/pi/FreiStat-Framework')
import time
import datetime
import os
import RPi.GPIO as GPIO

import serial
from FreiStat.Methods.run_cyclic_voltammetry import Run_CV
from FreiStat.Methods.run_chronoamperometry import Run_CA
from FreiStat.Serial_communication.serial_communication import Communication
from FreiStat.Data_storage.constants import*
from Python.FreiStat.Methods.run_sequence import Run_Sequence

x=-0.2 #set start potential
p=0

GPIO.setmode(GPIO.BCM)  #Input Output Pins

while(p<5):
	print(x)
	time.sleep(2)
	GPIO.setmode(GPIO.BCM) 
	serialPort=serial.Serial(port="/dev/ttyACM1",baudrate=9600,bytesize=8, timeout=2, stopbits=serial.STOPBITS_ONE) #serialport on which the MKZero is located
	datum=datetime.datetime.now()
	Zeit=(datum.strftime("%X"))
	datum=datetime.date.today()
	ZeroTrigger = 17
	Relay = 22
	GPIO.setup(ZeroTrigger, GPIO.OUT) #because loop needs clearance at the end and introduction in beginning
	GPIO.setup(Relay, GPIO.OUT)

	newpath = r'/home/pi/Desktop/%s' %datum  #create a folder or check if there already is one
	if not os.path.exists(newpath):
		os.makedirs(newpath)
	
	header="Voltage in mV \t time in ms \n"   #saves data in a txt format with the time the program startet(not the measurement)
	with open('{}/{}_{}_Volt.txt' .format(newpath,Zeit,x),'w') as f:
		f.write(header)

	run_CA = Run_CA(commnicationMode= FREISTAT_SERIAL ,
                mode= FREISTAT_STANDALONE
                )

	run_CV = Run_CV(commnicationMode= FREISTAT_SERIAL ,
                mode= FREISTAT_STANDALONE
                )

	GPIO.output(Relay, GPIO.HIGH)

	strExportPath = run_CA.start(Potential_Steps=[-0.3,0.8,-0.3,0.8,-0.3,0.8,-0.3,0.8,x],
								Pulse_Lengths=[0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,30],
								Sampling_Rate=0.003,
								Cycle= 1,
								CurrentRange= 45e-6,
								FixedWEPotential= True,
								MainsFilter= True,
								Sinc2_Oversampling= 222,
								Sinc3_Oversampling= 2,
								EnableOptimizer= True,
								LowPerformanceMode= True

                             )





	GPIO.output(Relay, GPIO.LOW) #--> unbinds WE WE
	
	GPIO.output(ZeroTrigger, GPIO.LOW) # --> Begins recording with MKRZERO 
	#time.sleep(1)
	GPIO.output(ZeroTrigger, GPIO.HIGH) #  --> Begins recording with MKRZERO 

	i=0

	while(i<100000):
		p=True	
		while(p==True):
		
			while(serialPort.in_waiting > 9):
		#serialPort.write(bytes(52))
				MKB=serialPort.inWaiting()
				serialString=serialPort.read(MKB)
				value=serialString.decode('Ascii')
				value=value.split(',')
				Potential=value[0]
				try:
					Time=value[1]
				except IndexError:
					pass
				with open('{}/{}_{}_Volt.txt' .format(newpath,Zeit,x),'a') as f:
					f.write(Potential+ '\t'+',\t' + Time)
				print(value)
			#print('end')
				p=False
	
		#time.sleep(0.5)
		i=i+1

	GPIO.output(ZeroTrigger, GPIO.LOW)
	p=p+1
	x=x+0.1 # increase start potential each loop by 0.1
	GPIO.cleanup() #cleans up GPIO-Pins
