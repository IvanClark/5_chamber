import serial
import time

# Set program parameters - some of these may need to be changed for your specific setup
switch_time = 3 #time of the switch in hours
post_switch_time = 10#time (h) from the switch to the end of the experiment
port1 = "COM4" #This may need to be changed - check the available port numbers in Device Manager
port2 = "COM5" #This may need to be changed - check the available port numbers in Device Manager
syringe_diameter = 14.43# This is correct of BD plastipak 10ml syringes (adjust for different syringe types)
fast_rate = 9 
slow_rate = 1
total_rate = fast_rate + slow_rate
switch_volume = 10 #Volume for the capacitance correction method (ul)
switch_rate = 100 #Flow rate for the capacitance correction method (ul/min)


#Set derived parameters
total_rate = fast_rate + slow_rate
diameter_string = "DIA " + str(syringe_diameter) + "\r"
fast_string = "RAT " + str(fast_rate) + "UM\r"
slow_string  = "RAT " + str(slow_rate) + "UM\r"


#Open the ports to control the pumps
p1=serial.Serial(port1,19200,timeout = 4,writeTimeout = 1)
p2=serial.Serial(port2,19200,timeout = 4,writeTimeout = 1)

#Ensure pumps are not running - this is necessary to set some of the parameters
p1.write(str.encode("STP\r"))
time.sleep(.05)
p2.write(str.encode("STP\r"))
time.sleep(.05)

#Set values for phase 1 (prior to the media switch)
p1.write(str.encode('PHN 1\r'))
time.sleep(.05)
p2.write(str.encode('PHN 1\r'))
time.sleep(.05)

#Ensure pumps are infusing (not withdrawing)
p1.write(str.encode("DIR INF\r"))
time.sleep(.05)
p2.write(str.encode("DIR INF\r"))
time.sleep(.05)

#Set the syringe diameter
p1.write(str.encode(diameter_string))
time.sleep(.05)
p2.write(str.encode(diameter_string))
time.sleep(.05)

#Set initial flow rates - 9ul/min for pump 1 (2% glucose) and 1ul/min for pump 2 (0.1% glucose)
p1.write(str.encode(fast_string))
time.sleep(.05)
p2.write(str.encode(slow_string))
time.sleep(.05)

#Set volumes to zero (off). Ensures the pumps run indefinitely
p1.write(str.encode("VOL 0\r"))
time.sleep(.05)
p2.write(str.encode("VOL 0\r"))
time.sleep(.05)

#Prepare the capacitance correcting method - write to pump phase 2
#Switching from p1:
p1SwitchRate = str(switch_rate);
p1SwitchDirection = 'DIR WDR\r';#Changes the pump direction to withdraw (not infuse)
p1SwitchVol = switch_volume
#Switching to p2:
p2SwitchRate = str(switch_rate + 10)
p2SwitchDirection = 'DIR INF\r'
capacitance_correction_time = switch_volume/switch_rate
switch_infuse_volume = capacitance_correction_time * total_rate # Volume that flows into the chambers during capacitance correction
p2SwitchVol = switch_volume + switch_infuse_volume
# Write values to phase 2
p1.write(str.encode('PHN 2\r'))
time.sleep(.05)
p1.write(str.encode('FUNRAT\r'))
time.sleep(.05)
p1.write(str.encode('RAT ' + str(p1SwitchRate) + 'UM\r'))
time.sleep(.05)
p1.write(str.encode('VOL' + str(p1SwitchVol) + '\r'))

p2.write(str.encode('PHN 2\r'))
time.sleep(.05)
p1.write(str.encode('FUNRAT\r'))
time.sleep(.05)
p2.write(str.encode('RAT ' + str(p2SwitchRate) + 'UM\r'))
time.sleep(.05)
p2.write(str.encode('VOL' + str(p2SwitchVol) + '\r'))
time.sleep(.05)

p1.write(str.encode(p1SwitchDirection))
p1.write(str.encode(p2SwitchDirection))
# Write values to phase 3 for period following the switch
p1.write(str.encode('PHN 3\r'))
time.sleep(.05)
p1.write(str.encode('FUN RAT\r'))
time.sleep(.05)
p1.write(str.encode(slow_string))
time.sleep(.05)
p1.write(str.encode('VOL 0\r'))
time.sleep(.05)

p2.write(str.encode('PHN 3\r'))
time.sleep(.05)
p2.write(str.encode('FUN RAT\r'))
time.sleep(.05)
p2.write(str.encode(fast_string))
time.sleep(.05)
p2.write(str.encode('VOL 0\r'))
time.sleep(.05)

#Return to phase 1 and start the pumps running
p1.write(str.encode("RUN1\r"))
time.sleep(.05)
p2.write(str.encode("RUN1\r"))
time.sleep(.05)

#All of the above commands could be run before the experiment is started.
#The following commands should be run at the same time as starting image acquisition

#Wait until the switch time
print("pumps running for " +str(switch_time*60*60) + "s\n")
time.sleep(switch_time*60*60)

#Run capacitance correction function
print("running capacitance corection\n")
p1.write(str.encode("RUN2\r"))
time.sleep(.05)
p2.write(str.encode("RUN2\r"))
time.sleep(.05)



#Wait until the end of the experiment
print("running post-switch flow\n")
time.sleep(post_switch_time*60*60)


#Stop the pumps
p1.write(str.encode("STP\r"))
time.sleep(.05)
p2.write(str.encode("STP\r"))
time.sleep(.05)
