# Library Imports
from time import ticks_us, ticks_ms, ticks_diff, ticks_add
from pyb import Pin
# Local File Imports
import encoder as e
import RomiMotor as m
import LineSensor as l
import cotask
import task_share

# Shares and queues created:
dutyL = task_share.Share('f', thread_protect=True, name="dutyL")
dutyR = task_share.Share('f', thread_protect=True, name="dutyR")
start = task_share.Share('b', thread_protect=True, name="start")
set_omegaL = task_share.Share('f', thread_protect=True, name="set_omegaL")
set_omegaR = task_share.Share('f', thread_protect=True, name="set_omegaR")
#omegaL = task_share.Queue('f', 100, thread_protect=True, name="omegaL")
#omegaR = task_share.Queue('f', 100, thread_protect=True, name="omegaR")


def circle_drive(speed, circleRadius, dir):
    '''!@brief Function that calculates Motor Controller Values for ROMI to drive in a circle of the given radius,
    in the given direction and speed.
    !@details Circle Drive Function takes speed in in/s, radius in in, dir = 1 for CCW, dir = 0 for CW
    to calculate the yaw rate to allow ROMI to drive in a circle with a given radius and in the specified speed.
    Depending on the the direction given ROMI will drive in a Counter-Clockwise Direction or Clockwise.
    !@return tuple
    '''
    # Romi radius = track width / 2
    romiRadius = 2.775
    # inches
    wheelRadius = 1.375
    # Direction YawRate Calculation
    if dir == 1:
        yaw_rate = speed / circleRadius
    else:
        yaw_rate = -speed / circleRadius

    # Left and Right Motor Speed Calculations
    speedL = speed - (romiRadius * yaw_rate)
    speedR = speed + (romiRadius * yaw_rate)

    # Angular Velocity Calculations
    omegaL = speedL / wheelRadius
    omegaR = speedR / wheelRadius

    # Left Duty Cycle Calculation
    dutyL = omegaL / 0.2528
    if dutyL > 100:
        dutyL = 100

    # Right Duty Cycle Calculation
    dutyR = omegaR / 0.2528
    if dutyR > 100:
        dutyR = 100
    return dutyL, dutyR, omegaL, omegaR

def straight_drive(speed):
    wheelRadius = 1.375
    speedL = speed
    speedR = speed
    omegaL = speedL / wheelRadius
    omegaR = speedR / wheelRadius
    dutyL = omegaL / 0.2528
    # Left Duty Cycle Calculation
    if dutyL > 100:
        dutyL = 100
    # Right Duty Cycle Calculation
    dutyR = omegaR / 0.2528
    if dutyR > 100:
        dutyR = 100
    return dutyL, dutyR, omegaL, omegaR

def spin(yaw_rate): # positive yaw rate for CCW
    # Romi radius = track width / 2
    romiRadius = 2.775
    # inches
    wheelRadius = 1.375

    omegaR = yaw_rate * romiRadius / wheelRadius
    omegaL = - omegaR

    # Left Duty Cycle Calculation
    dutyL = omegaL / 0.2528
    if dutyL > 100:
        dutyL = 100
    # Right Duty Cycle Calculation
    dutyR = omegaR / 0.2528
    if dutyR > 100:
        dutyR = 100
    return dutyL, dutyR, omegaL, omegaR

class MotL_control:
    '''
    !@brief A task class for Right Motor Control
    !@details Objects of this class can be used to apply to the Scheduler.
    '''

    def __init__(self, task_label, motL, encL):
        '''
        !@brief Left Motor Control Task 
        !@details Motor_L Control is the control tasks for the Left Motor of the ROMI robot. This
        takes in the ROMI motor object and the ROMI encoder object for the left wheel and creates
        a label for the task.
        '''
        self.task_label = task_label
        self.motL = motL
        self.encL = encL

    def run(self, shares):
        '''
        !@brief Runs the Motor L Control Task for Multi Tasking
        !@details The function sets the Angular Velocity, start, and the Duty cycle of the Left Motor
        The state is then initialized at state 0 where the encoder is at 0. After initializing data,
        state is change to the start where the Motor is enable and set to the duty cycle. State is change
        to state 2, for motor control implementation. The deltaT of the motor is updated until start is set
        to off where the state is sent to the stop state to stop motors then to the wait state until 
        re-initialization.
        !@shares represent the shared intertask variables representing the motor estimated duty cycles, set speeds,
        and an overall start flag.
        '''
        dutyL, start, set_omegaL = shares
        state = 0
        kff = 3.955
        ki = 0.5
        while True:
            # Implement FSM inside while loop
            if state == 0:
                # Run state zero code, any initializing
                self.encL.zero()  # zero out encoder
                if start.get() == 1:
                    state = 1
            elif state == 1:  # Start state, sets motor duty cycle and enables.
                now = ticks_us()
                self.motL.set_duty(dutyL.get())  # sets duty according to dutyL (share from comms state.)
                self.motL.enable()
                state = 2
            elif state == 2:  # Maintain state, where motor control is implemented.
                before = now  # for deltat calculation
                now = ticks_us()
                deltat = ticks_diff(now, before) / 10 ** 6
                self.encL.update()
                # FF + Integral control.
                dutyL.put(kff * set_omegaL.get() + (ki * (set_omegaL.get() - self.encL.get_speed(deltat))))
                self.motL.set_duty(dutyL.get())
                if start.get() == 0:  # if start is off, sets to state 3.
                    state = 3
            elif state == 3:  # stop state, disables motor.
                self.motL.disable()
                state = 4
            elif state == 4:  # Wait state
                if start.get() == 1:  # if start flag is set, move back to state 1. otherwise, stay waiting.
                    state = 1
            else:
                # If the state isnt 0, 1, or 2 we have an invalid state
                raise ValueError('Invalid state')
            yield state


class MotR_control:
    ''' !@brief A task class for Right Motor Control
        !@details Objects of this class can be used to apply to the Scheduler.
    '''

    def __init__(self, task_label, motR, encR):
        '''
        !@brief Right Motor Control Task
        !@details Motor_R Control is the control tasks for the Right Motor of the ROMI robot. This
        takes in the ROMI motor object and the ROMI encoder object for the right wheel and creates
        a label for the task.
        '''
        self.task_label = task_label
        self.motR = motR
        self.encR = encR
        print("initMotR")
    def run(self, shares):
        '''
        !@brief Runs the Motor R Control Task for Multi Tasking
        !@details The function sets the Angular Velocity, start, and the Duty cycle of the Right Motor
        The state is then initialized at state 0 where the encoder is at 0. After initializing data,
        state is change to the start where the Motor is enable and set to the duty cycle. State is change
        to state 2, for motor control implementation. The deltaT of the motor is updated until start is set
        to off where the state is sent to the stop state to stop motors then to the wait state until
        re-initialization.
        !@shares represent the shared intertask variables representing the motor estimated duty cycles, set speeds,
        and an overall start flag.
        '''
        dutyR, start, set_omegaR = shares
        state = 0
        kff = 3.955
        ki = 0.5
        while True:
            # Implement FSM inside while loop
            if state == 0:
                # Run state zero code, any initializing
                self.encR.zero()  # zero out encoder
                if start.get() == 1:
                    state = 1
            elif state == 1:  # Start state, sets motor duty cycle and enables.
                now = ticks_us()
                self.motR.set_duty(dutyR.get())  # sets duty according to dutyR (share from comms state.)
                self.motR.enable()
                state = 2
            elif state == 2:  # Maintain state, where motor control is implemented.
                before = now  # for deltat calculation
                now = ticks_us()
                deltat = ticks_diff(now, before) / 10 ** 6
                self.encR.update()
                # FF + Integral control.
                dutyR.put(kff * set_omegaR.get() + (ki * (set_omegaR.get() - self.encR.get_speed(deltat))))
                self.motR.set_duty(dutyR.get())
                if start.get() == 0:  # if start is off, sets to state 3.
                    state = 3
            elif state == 3:  # stop state, disables motor.
                self.motR.disable()
                state = 4
            elif state == 4:  # Wait state
                if start.get() == 1:  # if start flag is set, move back to state 1. otherwise, stay waiting.
                    state = 1
            else:
                # If the state isnt 0, 1, or 2 we have an invalid state
                raise ValueError('Invalid state')
            yield state

# Maybe change sensing task into a class instead of gen function, then we can take in the line sensor object initialized
# in main and create a self variable of that object, and access its methods within sensing.

class Sensing:
    ''' !@brief A task class for Sensing
        !@details Objects of this class can be used to apply to the Scheduler.
        '''

    def __init__(self, line_sensor):
        '''
        !@brief Initialization of Sensing Task returning an Object
        !@details Sensing is the Sense Task for the ROMI bot. This class will initialize parameters
        for the ROMI bump sensor, take in a user-input speed value, and set the speed values accordingly.
        !@line_sensor - an object of the LineSensor class is passed when initializing a sense object.
        allowing for methods of the LineSensor class to be called within the Sense task.
        '''
        self.line_sensor = line_sensor
        #Bump sensor init:
        sens1_c = Pin(Pin.cpu.C11, mode=Pin.OUT_PP)  # orange wire
        sens2_c = Pin(Pin.cpu.C8, mode=Pin.OUT_PP)  # red
        self.sens1_no = Pin(Pin.cpu.C12, mode=Pin.IN, pull=Pin.PULL_DOWN)  # brown wire
        self.sens2_no = Pin(Pin.cpu.C9, mode=Pin.IN, pull=Pin.PULL_DOWN)  # brown wire
        sens1_c.value(1)
        sens2_c.value(1)
        #Speed set:
        self.speed = float(input("Enter speed in inches/s: "))
        self.set_dutyL, self.set_dutyR, self.set_omegaL, self.set_omegaR = straight_drive(self.speed)
        self.wall_done = 0  #boolean, true when wall has been passed.
    def run(self, shares): # if code == 1, turn left. if -1, turn right. if 0, drive straight.
        '''
        !@brief Runs the Sense Task for Multi Tasking
        !@details This function takes in the shared variables used for inter-task communication, and starts by
        initializing several local variables used for course navigation. Initialized and speed set at state 0, line
        sense control at state 1, wall navigation (in 4 segments) at states 2-5, and finish reached at state 6.
        !@shares represent the shared intertask variables representing the motor estimated duty cycles, set speeds,
        and an overall start flag.
        '''
        dutyL, dutyR, start, set_omegaL, set_omegaR, = shares
        state = 0
        start.put(0)
        centroid = 0
        dash_done = 0
        starttime = ticks_ms() #Used to segment speeds: faster speed for dashed lines nav, slower for tight turns.

        while True:
            if state == 0: # INIT and set speed state.
                if dash_done == 1:
                    self.set_dutyL, self.set_dutyR, self.set_omegaL, self.set_omegaR = straight_drive(3)
                dutyL.put(self.set_dutyL)
                dutyR.put(self.set_dutyR)
                set_omegaL.put(self.set_omegaL+1.2)
                set_omegaR.put(self.set_omegaR)
                start.put(1)
                print("state0Sense")
                state = 1
            elif state == 1:  #Line sensing state, await bump or line crossing.
                print("state1sense")
                if dash_done == 0:
                    if ticks_diff(ticks_ms(),starttime) >= 15000:
                        state = 0
                        dash_done = 1

                past_centroid = centroid # Calculate past centroid to slow turning, limiting overshooting the line.
                centroid, line = self.line_sensor.centroid3()
                chng_centroid = abs(centroid) - abs(past_centroid) # used to limit overcorrection.

                # Line sense control: Changes set speed based on weighted centroid values.
                if chng_centroid >= 0: #If change in centroid is positive, the current centroid is higher (worse) than past_centroid.

                    if abs(centroid) <= 0:   #drive straight (all white or all black)
                        set_omegaR.put(self.set_omegaR)
                        set_omegaL.put(self.set_omegaL+1.2) #Adjustment based on different motor dynamics.
                    elif abs(centroid) > 0:
                        currentR = set_omegaR.get()
                        currentL = set_omegaL.get()
                        set_omegaR.put(currentR + .065 * centroid)  # edit if turning too fast / slow
                        set_omegaL.put(currentL - .065 * centroid)
                else:           # Else, meaning change in centroid is negative, current centroid is lower (better), slow down turn.
                    set_omegaR.put(self.set_omegaR)
                    set_omegaL.put(self.set_omegaL)

                #if wall already passed, and line crossed: means we're at the finish line.
                if line and self.wall_done == 1:
                    begin = ticks_ms()
                    state = 6

                if self.sens1_no.value() or self.sens2_no.value():   #if bump triggered, go to state 2 and set wall_done
                    state = 2
                    begin = ticks_ms()
                    self.wall_done = 1

            elif state == 2:  # Bump triggered. Backup 3 inches, turn 90deg CCW, drive in half circle, drive straight, hit line.
                set_dutyL, set_dutyR, setL, setR = straight_drive(-3) # -3in/s

                set_omegaR.put(setR)
                set_omegaL.put(setL)

                if ticks_diff(ticks_ms(), begin) >= 1500:
                    state = 3
                    begin = ticks_ms()
            elif state == 3: # Finished backing up, start pivot.
                set_dutyL, set_dutyR, setL, setR = spin(-3.14) #Spin at pi rad/s for .5s (90deg turn)
                set_omegaR.put(setR)
                set_omegaL.put(setL)

                if ticks_diff(ticks_ms(), begin) >= 500:
                    state = 4
                    begin = ticks_ms()
            elif state == 4: # Turn in large circle, CCW around box.
                set_dutyL, set_dutyR, setL, setR = circle_drive(5, 40, 1)
                set_omegaR.put(setR)
                set_omegaL.put(setL)

                if ticks_diff(ticks_ms(), begin) >= 7500: #8000
                    state = 5
                    begin = ticks_ms()

            elif state == 5: # Drive straight at 3in/s for 3s, then move back to line following.
                set_dutyL, set_dutyR, setL, setR = straight_drive(3)  # 3in/s
                set_omegaR.put(setR)
                set_omegaL.put(setL)
                if ticks_diff(ticks_ms(), begin) >= 3000:
                    state = 0

            elif state == 6: #Line crossed after wall complete, in finish box.
                # Could be improved by adding delay, so Romi is fully in finish box, rather than turning upon arrival.
                set_dutyL, set_dutyR, setL, setR = spin(-3.14) ##Spin at pi rad/s for 1s (180deg turn)

                set_omegaR.put(setR)
                set_omegaL.put(setL)

                if ticks_diff(ticks_ms(), begin) >= 1000:
                    state = 0
                    begin = ticks_ms()

            elif state == 7: #Finished state, set speeds and start off.
                start.put(0)
                set_omegaR.put(0)
                set_omegaL.put(0)

            yield state
