
import sys
import os
import rpyc
import time
import re
from RR_API import *

#Roborealm Connect
rr = RR_API()
rr.Connect("localhost")
c = rpyc.classic.connect("10.0.0.68")

#Brick Connect
ev3=c.modules["ev3dev.ev3"]


#Motor Config START

links=ev3.LargeMotor('outB')
links.connected
links.reset()# setzt position auf null
links.stop_command="brake"
links.speed_regulation_enabled="off"


rechts=ev3.LargeMotor('outC')
rechts.connected
rechts.reset()# setzt position auf null
rechts.stop_command="brake"
rechts.speed_regulation_enabled="off"



mm = ev3.MediumMotor('outA')
mm.connected
mm.reset()# setzt position auf null
mm.stop_command="brake"
mm.polarity="inversed"
mm.speed_regulation_enabled="on"

#Motor Config END

def FastRead(infile):
    infile.seek(0)    
    value = int(infile.read().decode().strip())
    return(value)


def gripon():
    pos=-600
    print (mm.position_sp)
    mm.position_sp=pos
    mm.run_to_rel_pos(speed_sp=300)
    while mm.state:
        time.sleep(2)
        print (mm.position)
        break
 
def gripoff():
    pos=600
    mm.position_sp=pos
    mm.run_to_abs_pos(speed_sp=300)
    while mm.state:
        time.sleep(2)
        print (mm.position)
        break

def drive_loop():
    print "drive_loop"
    robot_x = "%d"% float(rr.GetVariable("robot_x").replace(',', '.'))
    robot_y = "%d"% float(rr.GetVariable("robot_y").replace(',', '.'))
    robot_x=int(robot_x)
    robot_y=int(robot_y)

    if robot_y > 350 or robot_y > 310 or robot_x < 10 or robot_y < 10:
        rechts.run_direct(duty_cycle_sp=-50)
        links.run_direct(duty_cycle_sp=-50)
        time.sleep(3)
        rechts.run_direct(duty_cycle_sp=50)
        links.run_direct(duty_cycle_sp=-50)
        time.sleep(3)
    else:
        rechts.run_direct(duty_cycle_sp=50)
        links.run_direct(duty_cycle_sp=50)


def pathfollow():
    print "pathfollow"
    right_motor=0
    left_motor=0
    if rr.GetVariable("robot_orientation") <> "":
        robotOrientation = "%d"% float(rr.GetVariable("robot_orientation").replace(',', '.'))
        desiredOrientation = "%d"% float(rr.GetVariable("plan_orientation").replace(',', '.'))
        robotOrientation=int(robotOrientation)
        desiredOrientation=int(desiredOrientation)
    else:
        robotOrientation=0
        desiredOrientation=0


    
    correction=desiredOrientation - robotOrientation
    robotOrientation = (robotOrientation / 20)  * 20
    desiredOrientation = (desiredOrientation / 20)  * 20
    diff = abs(desiredOrientation - robotOrientation)
    #Forward with correction
    if desiredOrientation == robotOrientation:
        right_motor=60
        left_motor=60
        if correction < 0:
            right_motor=60 - (correction * -1)
            left_motor=60
        if correction > 0:
            right_motor=60 + correction
            left_motor=60


    #Turn Left
    elif desiredOrientation > robotOrientation and diff < 180 or  desiredOrientation < robotOrientation and diff >= 180:
        left_motor=rev_left_speed
        right_motor=right_speed
    #Turn Right
    else:
        #' if we don't turn one way then default to the other
        left_motor=left_speed
        right_motor=rev_right_speed
    print left_motor, right_motor,  correction, diff, desiredOrientation, robotOrientation
    rechts.run_direct(duty_cycle_sp=left_motor)
    links.run_direct(duty_cycle_sp=right_motor)
    if rr.GetVariable("plan_orientation") == "-1":
        return 0
    else:
        return 1


def pixymove():
    directory="/sys/bus/i2c/devices/i2c-3/3-0001/lego-sensor/sensor0/"
    pixy_width=FastRead(c.builtin.open(directory + "value3"))
    pixy_sig=1
    pixy_sig=int(pixy_sig)
    pixy_count=FastRead(c.builtin.open(directory + "value0"))
    pixy_x=FastRead(c.builtin.open(directory + "value2"))
    pixy_y=FastRead(c.builtin.open(directory + "value3"))
    pixy_height=FastRead(c.builtin.open(directory + "value4"))
    minheight=30
    sig=1
    print pixy_sig, pixy_count, pixy_x, pixy_y, pixy_width, pixy_height

    if pixy_width > 95 and pixy_sig == 1 and pixy_count == 1:
        print "done"
        rechts.run_direct(duty_cycle_sp=0)
        links.run_direct(duty_cycle_sp=0)
        return 1
    else:
        
        if pixy_sig == 1 and pixy_count == 1:
            if pixy_x > 1 and pixy_x < 130  and pixy_height > minheight and pixy_sig == sig and pixy_count == 1:
                rechts.run_direct(duty_cycle_sp=-30)
                links.run_direct(duty_cycle_sp=30)

            elif pixy_x > 190 and pixy_x < 320 and pixy_height > minheight and pixy_sig == sig and pixy_count == 1:
                rechts.run_direct(duty_cycle_sp=30)
                links.run_direct(duty_cycle_sp=-30)
            
            elif pixy_width < 95  and pixy_sig == 1 and pixy_count == 1:
                rechts.run_direct(duty_cycle_sp=50)
                links.run_direct(duty_cycle_sp=50)
            else:
                rechts.run_direct(duty_cycle_sp=-50)
                links.run_direct(duty_cycle_sp=-50)
        return 0    

def pixymove_rr():
    print "pixymove_rr"
    if rr.GetVariable("pixy_width") <> "":
        pixy_width="%d"% float(rr.GetVariable("pixy_width").replace(',', '.'))
        pixy_width=int(pixy_width)
        pixy_sig="%d"% float(rr.GetVariable("pixy_sig").replace(',', '.'))
        pixy_sig=int(pixy_sig)
        pixy_count="%d"% float(rr.GetVariable("pixy_count").replace(',', '.'))
        pixy_count=int(pixy_count)
        pixy_x="%d"% float(rr.GetVariable("pixy_x").replace(',', '.'))
        pixy_x=int(pixy_x)
        pixy_y="%d"% float(rr.GetVariable("pixy_y").replace(',', '.'))
        pixy_y=int(pixy_y)
        pixy_height="%d"% float(rr.GetVariable("pixy_height").replace(',', '.'))
        pixy_height=int(pixy_height)
    else:
        pixy_width=0
        pixy_sig=0
        pixy_count=0
        pixy_x=0
        pixy_y=0
        pixy_height=0

        
    minheight=30
    sig=1
    print pixy_sig, pixy_count, pixy_x, pixy_y, pixy_width, pixy_height
    if pixy_count==0:
        return 0
    
    if pixy_width > 80 and pixy_sig == 1 and pixy_count == 10:

        rechts.run_direct(duty_cycle_sp=0)
        links.run_direct(duty_cycle_sp=0)
        return 3
    else:
        
        if pixy_sig == 1 and pixy_count == 10:
            if pixy_x > 1 and pixy_x < 130  and pixy_height > minheight and pixy_sig == sig and pixy_count == 10:
                rechts.run_direct(duty_cycle_sp=-30)
                links.run_direct(duty_cycle_sp=30)

            elif pixy_x > 190 and pixy_x < 320 and pixy_height > minheight and pixy_sig == sig and pixy_count == 10:
                rechts.run_direct(duty_cycle_sp=30)
                links.run_direct(duty_cycle_sp=-30)
            
            elif pixy_width < 80  and pixy_sig == 1 and pixy_count == 10:
                rechts.run_direct(duty_cycle_sp=50)
                links.run_direct(duty_cycle_sp=50)
            else:
                rechts.run_direct(duty_cycle_sp=-50)
                links.run_direct(duty_cycle_sp=-50)
        return 2



    

###### MAIN

left_speed = 30
right_speed = 30
rev_left_speed = -10
rev_right_speed = -10
stopped = 0
gripper=0

links.run_direct(duty_cycle_sp=0)
rechts.run_direct(duty_cycle_sp=0)

checkpixy=0
checkfollow=0
step=0
rr.SetVariable("pathreset", "1");
time.sleep(1)
rr.DeleteVariable("pathreset");

rr.SetVariable("target", "1");
time.sleep(1)
rr.DeleteVariable("target");

while 1:

    print step
    #drive_loop()
    #if pixymove_rr() == 1:
        #print "blub"
        #pixymove()

    #Manual Button Control in loop
    if step==2:
        step=pixymove_rr()
        
    elif step==3:
        gripon()
        time.sleep(1)
        rr.SetVariable("pathreset", "1");
        time.sleep(1)
        rr.DeleteVariable("pathreset");
        time.sleep(1)
        rr.SetVariable("base", "1");
        time.sleep(1)
        rr.DeleteVariable("base");
        step=4
    elif step==4:
        if pathfollow() == 0:
            step=5
    elif step==5:
        links.run_direct(duty_cycle_sp=0)
        rechts.run_direct(duty_cycle_sp=0)
        gripoff()
        step=6
    elif step==6:
        print "END Prog"
    elif step==993:
        gripon()
        time.sleep(1)
        links.run_direct(duty_cycle_sp=60)
        rechts.run_direct(duty_cycle_sp=-60)
        time.sleep(1)
        links.run_direct(duty_cycle_sp=60)
        rechts.run_direct(duty_cycle_sp=60)
        time.sleep(1)
        links.run_direct(duty_cycle_sp=0)
        rechts.run_direct(duty_cycle_sp=0)
        gripoff()
        time.sleep(1)
        links.run_direct(duty_cycle_sp=-60)
        rechts.run_direct(duty_cycle_sp=-60)
        time.sleep(1)
        links.run_direct(duty_cycle_sp=60)
        rechts.run_direct(duty_cycle_sp=-60)
        time.sleep(2)
        links.run_direct(duty_cycle_sp=60)
        rechts.run_direct(duty_cycle_sp=60)
        time.sleep(1)
        links.run_direct(duty_cycle_sp=0)
        rechts.run_direct(duty_cycle_sp=0)
        step=0
    elif rr.GetVariable("control") == "7":
        step=2
    elif rr.GetVariable("control") == "1":
        links.run_direct(duty_cycle_sp=-60)
        rechts.run_direct(duty_cycle_sp=-60)
    elif rr.GetVariable("control") == "2":
        links.run_direct(duty_cycle_sp=60)
        rechts.run_direct(duty_cycle_sp=60)
    elif rr.GetVariable("control") == "3":
        links.run_direct(duty_cycle_sp=60)
        rechts.run_direct(duty_cycle_sp=-60)
    elif rr.GetVariable("control") == "4":
        links.run_direct(duty_cycle_sp=-60)
        rechts.run_direct(duty_cycle_sp=60)
    elif rr.GetVariable("control") == "6":
        gripon()
    elif rr.GetVariable("control") == "5":
        gripoff()
    #Start Main APP ResetButton
    elif rr.GetVariable("plan_orientation") == "-1":
        print ""
        links.run_direct(duty_cycle_sp=0)
        rechts.run_direct(duty_cycle_sp=0)
    else:
        if pathfollow() == 0:
            print "start pathfollow"
            links.run_direct(duty_cycle_sp=0)
            rechts.run_direct(duty_cycle_sp=0)
            #gripon()
            print "done"
            step=2

            
        elif rr.GetVariable("control") == "7" or checkpixy==1:
            step=2


#gripon()
#time.sleep(2)
#gripoff()

#m = ev3.LargeMotor('outB')
#m.connected
#m.run_timed(time_sp=3000, duty_cycle_sp=75)

#rr.SetVariable("right_motor", 20)



rr.close()
