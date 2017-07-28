import PiIO
import maestro
import xbox
import drive
import time

# CONSTANTS
LEFT_MOTORS = 1
RIGHT_MOTORS = 0
THROWER = 2
CAM = 3
THROWER_MAX = 9200
THROWER_STOP = 6000
THROWER_RANGE = 3200
CAM_REV = 2800
CAM_FWD = 9000
CAM_STOP = 6000

# VARIABLES
throwSpeed = 3
currentThrower = THROWER_MAX # Initial thrower set to max power

# BOOLEANS
isStarted = False # Press Start to enable the robot
driveEnabled = True
speedToggle = True # True = Full Speed; False = Slow Mode
compressorEnabled = False
PressedY = False # Allows Y to be called on rising edge
throwerEnabled = False
pressedA = False # Allows A to be called on rising edge
pressedBack = False # Allows Back to be called on rising edge
pressedLT = False
hornOff = True


j = xbox.Joystick()
motors = maestro.Controller()
drive = drive.DriveTrain(motors, LEFT_MOTORS, RIGHT_MOTORS)
prevTime = time.time()

try:
    winch      = PiIO.Spike(1)
    compressor = PiIO.Spike(2)
    cannonl    = PiIO.Spike(3)
    cannonr    = PiIO.Spike(4)
    
    upperLimit = PiIO.Switch(1)
    lowerLimit = PiIO.Switch(2)
    camLimit   = PiIO.Switch(3)
    pressureSw = PiIO.Switch(4)
    
except:
    raise
# **MAINE LOOP**
print "*************************** NOTICE ******************************"
print "You are running sashaOld.py.  This file contains the old drive system."
print "It is included for drivers who haven't used the new drive code."
print "As this code lacks many of the safety features added in the new version,"
print "it has been deprecated and its use is NOT RECOMMENDED."
print "The current file is listed as sasha.py and should boot upon startup."
print "*****************************************************************"
print " "

time.sleep(10)
print "Sasha rises!"
print "Press Start to enable."
try:
    while True:

        if isStarted and j.connected():
            ### Drive Command ###
            if driveEnabled:
                if speedToggle:
                    if abs(j.leftX()) <= .20 and abs(j.leftY()) <= .20:
                        drive.drive(0, 0)
                    else:
                        drive.drive(j.leftX(), j.leftY())
                else:
                    if abs(j.leftX()) <= .20 and abs(j.leftY()) <= .20:
                        drive.drive(0, 0)
                    else:
                        drive.drive(j.leftX(), j.leftY() * .4)    
            else:
                drive.drive(0, 0)

            ### Speed toggle & Drive Control ###
            if j.Back():
                driveEnabled = False
                # print "Driving Disabled"
            if j.Start():
                driveEnabled = True
                # print "Driving Enabled"
                if j.X():
                    speedToggle = True
                    # print "FULL SPEED AHEAD!"
                elif j.B():
                    speedToggle = False
                    # print "Slow Driving Mode"
                else:
                    speedToggle = speedToggle
                
            ### Raise and Lower Frisbee Thrower ###
            if j.dpadUp() and upperLimit.open():
                winch.rev()
            elif j.dpadDown() and lowerLimit.open():
                winch.fwd()
            else:
                winch.stop()


            """ New Thrower Code """
            ### Start And Stop Thrower###
            if j.A():
                if pressedA == False:
                    if throwerEnabled == False:
                        motors.setTarget(THROWER, currentThrower)
                        throwerEnabled = True
                        print "Thrower On"
                    else:
                        motors.setTarget(THROWER, THROWER_STOP)
                        throwerEnabled = False
                        print "Thrower Off"
                    pressedA = True
            else:
                pressedA = False

            ### Speed Of Thrower Motor ### 
            if j.leftTrigger() >= .2 and throwerEnabled == True:
                if pressedLT == False:
                    if throwSpeed < 3:
                        throwSpeed = throwSpeed + 1
                    else:
                        throwSpeed = 0
                    currentThrower = int(THROWER_STOP + (THROWER_RANGE * (.55 + .15 * throwSpeed)))
                    motors.setTarget(THROWER, currentThrower)
                    print "throwSpeed ="
                    print throwSpeed
                    print (.55 + .15 * throwSpeed)
                    pressedLT = True
            else:
                pressedLT = False
                        
            ### Launch frisbee ###
            if j.rightTrigger() > 0.2:
		prevTime = time.time()
                if j.B():
                    motors.setTarget(CAM, CAM_REV)
                    print "Unjam"
                elif throwerEnabled:
                    motors.setTarget(CAM, CAM_FWD)
                    print "Throw"
            elif camLimit.closed() or (time.time() - prevTime >= 1):
                motors.setTarget(CAM, CAM_STOP)
            """End of new thrower code"""


            ### Compressor ###
            if j.Y():
                if pressedY == False:
                    if compressorEnabled == False:
                        compressorEnabled = True
                        #print "Compressor Enabled"
                    else:
                        compressorEnabled = False
                        #print "Compressor Disabled"
                    pressedY = True
            else:
                pressedY = False
                
            if compressorEnabled == False or pressureSw.open():
                compressor.stop()
                compressorEnabled = False
                #print "Compressor Stopped"
            else:
                compressor.fwd()
                #print "Compressor Started"
                        
            ### T-Shirt Cannons ###
            if j.rightBumper(): # and hornOff == False:
                 cannonr.fwd()
            else:
                cannonr.stop()

            if j.leftBumper():
                cannonl.fwd()
            else:
                cannonl.stop()
                
        # Stop motors if controller is not connected.
        else:
            # Stop drive
            drive.drive(0, 0)
            # Stop winch
            winch.stop()
            # Stop thrower
            motors.setTarget(THROWER, THROWER_STOP)
            # Stop cam
            motors.setTarget(CAM, CAM_STOP)
            # Stop compressor
            compressor.stop()
            # print "Not Connected."
            
        ### Robot Start Boolean ###
        if j.Start():
            isStarted = True
            #print "Start"

        # Time interval before next loop begins.
        time.sleep(0.033)
except:
        winch.stop()
        motors.setTarget(CAM, CAM_STOP)
        motors.setTarget(THROWER, THROWER_STOP)
        compressor.stop()
        drive.close()
        motors.close()
        j.close()
        PiIO.close()
        raise
