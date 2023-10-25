from gpiozero import LED
import sys
sys.path.append('/home/pi/FreiStat-Framework/Python')  #adds dependencies
sys.path.append('/usr/lib/python3/dist-packages')
import time
import datetime
import os

import serial
from FreiStat.Methods.run_cyclic_voltammetry import Run_CV
from FreiStat.Methods.run_chronoamperometry import Run_CA
from FreiStat.Serial_communication.serial_communication import Communication
from FreiStat.Data_storage.constants import*

serialPort=serial.Serial(port="/dev/ttyACM0",baudrate=9600,bytesize=8, timeout=2, stopbits=serial.STOPBITS_ONE) #serialport on which the MKZero is located
datum=datetime.datetime.now()
Zeit=(datum.strftime("%X"))
datum=datetime.date.today()
ZeroTrigger = LED(17)
Relay = LED(22)

newpath = r'/home/pi/Desktop/%s' %datum  #create a folder or check if there already is one
if not os.path.exists(newpath):
	os.makedirs(newpath)
	
header="Voltage in mV \t time in ms \n"   #saves data in a txt format with the time the program startet(not the measurement)
with open('{}/{}.txt' .format(newpath,Zeit),'w') as f:
	f.write(header)

run_CA = Run_CA(commnicationMode= FREISTAT_SERIAL ,
                mode= FREISTAT_STANDALONE
                )

run_CV = Run_CV(commnicationMode= FREISTAT_SERIAL ,
                mode= FREISTAT_STANDALONE
                )
Relay.on()  #combines the Workingelectrodes


strExportPath = run_CA.start(Potential_Steps=[-0.3,0.8,-0.3,0.8,-0.3,0.8,-0.3,0.8,0.3],
							 Pulse_Lengths=[0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,20],
							 Sampling_Rate=0.003,
                             Cycle= 1,
                             CurrentRange= 45e-6,
                             FixedWEPotential= True,
                             MainsFilter= True,
                             Sinc2_Oversampling= 222,
                             Sinc3_Oversampling= 2,
                             EnableOptimizer= True,
                             LowPerformanceMode= False
                             )




Relay.off() # Relay.on() --> binds WE to WE
ZeroTrigger.off() # ZeroTrigger.off() --> Begins recording with MKRZERO 
time.sleep(1)
ZeroTrigger.on() # ZeroTrigger.off() --> Begins recording with MKRZERO 
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
