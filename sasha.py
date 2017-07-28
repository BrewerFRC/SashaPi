################################
##         sasha.py           ##
################################
## Orange Chaos (4564) 2013   ##
## competiton robot.          ##
##                            ##
## Authors: Steven Jacobs     ##
##          & Connor Billings ##
##                            ##
## Published: July, 2014      ##
## Updated: July 27, 2017     ##
################################

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
THROWER_MIN = 7760 # Minimum Thrower Speed (55%)
THROWER_STOP = 6000
THROWER_RANGE = 3200
THROWER_INC = 160 # Thrower Increment (5%)
CAM_REV = 2800
CAM_FWD = 9000
CAM_STOP = 6000

# VARIABLES
throwSpeed = 3
currentThrower = THROWER_MAX # Initial thrower set to max power

# BOOLEANS
isStarted = False # Press Start to enable the robot
driveEnabled = True # also controls the winch
speedToggle = True # True = Full Speed; False = Slow Mode
compressorEnabled = False
throwerEnabled = False


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
                        drive.drive(j.leftX() * .5, j.leftY() * .4)    
            else:
                drive.drive(0, 0)

            ### Speed toggle & Drive Control ###
            if j.Back():
                driveEnabled = False
                # print "Driving Disabled"
                winch.stop()
                compressor.stop()
                compressorEnabled = False
                #print "Compressor disabled"
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
            if j.dpadUp() and upperLimit.open() and driveEnabled:
                winch.rev()
            elif j.dpadDown() and lowerLimit.open() and driveEnabled:
                winch.fwd()
            else:
                winch.stop()
            

            #########################################################
	    ## Connor's Thrower Code
            #########################################################
			
            ### Start And Stop Thrower ###
            if j.whenA():
                throwerEnabled = not throwerEnabled

            
            ### Speed Of Thrower Motor ###
            if throwerEnabled and j.rightThumbstick():
                if j.whenRightJoystickUp() and (currentThrower + THROWER_INC <= THROWER_MAX):
                    currentThrower = currentThrower + THROWER_INC
                    #print "Increment by 5%"
                if j.whenRightJoystickDown() and (currentThrower - THROWER_INC >= THROWER_MIN):
                    currentThrower = currentThrower - THROWER_INC
                    #print "Decrement by 5%"

            
            ### Set thrower to max or min speed. ###
            if j.rightX() > 0.8 and j.rightThumbstick() and throwerEnabled:
                    currentThrower = THROWER_MAX
                    #print "MAX Speed"
            if j.rightX() < -0.8 and j.rightThumbstick() and throwerEnabled:
                    currentThrower = THROWER_MIN
                    #print "MIN Speed"
			
            ### Run the thrower ###
            if throwerEnabled:
                motors.setTarget(THROWER, currentThrower)
                #print "motor on" 
                #print currentThrower 
            else:
                motors.setTarget(THROWER, THROWER_STOP)
				
            ### Launch frisbee ###
            if j.rightTrigger() > 0.2:
		prevTime = time.time()
                if j.B():
                    motors.setTarget(CAM, CAM_REV)
                    #print "Unjam"
                elif throwerEnabled:
                    motors.setTarget(CAM, CAM_FWD)
                    #print "Throw"
            elif camLimit.closed() or (time.time() - prevTime >= 1):
                motors.setTarget(CAM, CAM_STOP)
            
	    #########################################################
            ## End Thrower Code
            #########################################################


            ### Compressor ###
            if j.whenY() and driveEnabled:
                compressorEnabled = not compressorEnabled

                
            if (not compressorEnabled) or (not driveEnabled) or pressureSw.open():
                compressor.stop()
                compressorEnabled = False
                #print "Compressor Stopped"
            else:
                compressor.fwd()
                #print "Compressor Started"
                        
            ### T-Shirt Cannons ###
            if j.rightBumper() and driveEnabled:
                 cannonr.fwd()
                 #print "Right cannon"
            else:
                cannonr.stop()

            if j.leftBumper() and driveEnabled:
                cannonl.fwd()
                #print "Left cannon"
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
            # Reset Booleans
            isStarted = False
            driveEnabled = False
            compressorEnabled = False
            throwerEnabled = False 
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
