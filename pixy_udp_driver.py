
import socket
import subprocess
import time
import os
import sys  #for exit
 
# create dgram udp socket
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
except socket.error:
    print('Failed to create socket')
    sys.exit()

host = '10.0.0.17';
port = 9090;

# Pixy Python SWIG get blocks example #
def FastRead(infile):
    infile.seek(0)    
    value = int(infile.read().decode().strip())
    return(value)

print("Pixy Python SYS Driver")

# Initialize Pixy Interpreter thread #


# Wait for blocks #
while 1:
    directory="/sys/bus/i2c/devices/i2c-3/3-0001/lego-sensor/sensor1/"
    count=15

    if count > 0:
        #print "OK"
        """
        count=os.popen("cat " + directory + "value0").read()
        frame=os.popen("cat " + directory + "value1").read()
        typea=1
        signature=1
        x=os.popen("cat " + directory + "value2").read()
        y=os.popen("cat " + directory + "value3").read()
        width=os.popen("cat " + directory + "value4").read()
        height=os.popen("cat " + directory + "value5").read()
        """
        count=FastRead(open(directory + "value0"))
        frame=FastRead(open(directory + "value1"))
        typea=1
        signature=1
        x=FastRead(open(directory + "value2"))
        y=FastRead(open(directory + "value3"))
        width=FastRead(open(directory + "value4"))
        height=FastRead(open(directory + "value5"))
        #time.sleep(0.1)


        message=str(count) + str(frame) + ';' + str(typea) + ';' + str(signature) + ';' + str(x) + ';' + str(y) +   ';' + str(width) + ';' + str(height) +  '\r\n'
        #print message

        s.sendto(message.encode(),(host, port)) 


