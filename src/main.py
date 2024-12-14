# Library Imports
from pyb import Pin, Timer, I2C
from time import ticks_us, ticks_ms, ticks_diff, ticks_add, sleep_ms
import math
from array import array

# Local File and Driver Imports
import encoder as e
import RomiMotor as m
import HC06 as s
import BNO055 as i
import cotask
import pyb
import gc
import ROMI_tasks as c
import task_share
import LineSensor as ls
##LINE SENSOR PINS:
#SENSOR NUMBER: 1    2    3    4    5    6    7    8
#PIN NUMBER:    B2   B1  B15  B14   C0   C1   C2   C3

if __name__ == '__main__':
    # Establishing Serial Bluetooth Connection
    uart = s.HC06()
    uart.estREPL()

    # Timer Instantiation and AR and PS Values
    AR = 65535
    PS = 0
    tim_L = Timer(4, freq=20000)
    tim_R = Timer(8, freq=20000)

    # Left and Right Motor Object
    mot_L = m.RomiMotor(tim_L, Pin.cpu.B6, Pin.cpu.B7, Pin.cpu.A10)
    mot_R = m.RomiMotor(tim_R, Pin.cpu.C6, Pin.cpu.C7, Pin.cpu.B0)

    # Right and Left Motor Encoder Objects
    enc_L = e.Encoder(3, Pin.cpu.A6, Pin.cpu.A7, AR, PS)
    enc_R = e.Encoder(2, Pin.cpu.A0, Pin.cpu.A1, AR, PS)

    # Line Sensor Object
    lsVdd = Pin(Pin.cpu.C4, mode=Pin.OUT_PP)
    lsLED = Pin(Pin.cpu.B13, mode=Pin.OUT_PP)
    lsVdd.high()
    lsLED.high()
    linesens = ls.LineSensor()
    linesens.sensConfig(Pin.cpu.B2, Pin.cpu.B1, Pin.cpu.B15, Pin.cpu.B14,
                        Pin.cpu.C0, Pin.cpu.C1, Pin.cpu.C2, Pin.cpu.C3)

    # Disable Motors
    mot_L.disable()
    mot_R.disable()

    # Motor Control Tasks and Comms Tasks
    control_L = c.MotL_control(1, mot_L, enc_L)
    control_R = c.MotR_control(1, mot_R, enc_R)
    #comms = c.Comms()
    sense = c.Sensing(linesens)

    # Create shares and queues:
    dutyL = task_share.Share('f', thread_protect=True, name="dutyL")
    dutyR = task_share.Share('f', thread_protect=True, name="dutyR")
    set_omegaL = task_share.Share('f', thread_protect=True, name="set_omegaL")
    set_omegaR = task_share.Share('f', thread_protect=True, name="set_omegaR")
    start = task_share.Share('b', thread_protect=True, name="start")
    #omegaL = task_share.Queue('f', 100, thread_protect=True, name="omegaL") #Used queues for testing and debugging
    #omegaR = task_share.Queue('f', 100, thread_protect=True, name="omegaR") #but not in final run.

    # Create the tasks. If trace is enabled for any task, memory will be
    # allocated for state transition tracing, and the application will run out
    # of memory after a while and quit. Therefore, use tracing only for
    # debugging and set trace to False when it's not needed
    control_L = cotask.Task(control_L.run, name="control_L", priority=2, period=20,
                            profile=True, trace=False, shares=(dutyL, start, set_omegaL))
    control_R = cotask.Task(control_R.run, name="control_R", priority=2, period=20,
                            profile=True, trace=False, shares=(dutyR, start, set_omegaR))
    sense = cotask.Task(sense.run, name="sense", priority=2, period=100,
                        profile=True, trace=False, shares=(dutyL, dutyR, start, set_omegaL, set_omegaR))

    #Used Comms task for printing during testing and debugging, not in final run.
    # comms = cotask.Task(comms.run, name="comms", priority=1, period=10,
    #                    profile=True, trace=False, shares=(dutyL, dutyR, start, set_omegaL, set_omegaR, omegaL, omegaR))

    cotask.task_list.append(control_L)
    cotask.task_list.append(control_R)
    cotask.task_list.append(sense)
    gc.collect()  # Run the memory garbage collector to ensure memory is as defragmented as possible

    # Run the scheduler with the chosen scheduling algorithm. Quit if ^C pressed
    begin = input("Start")
    start.put(0)
    while True:
        try:
            cotask.task_list.pri_sched()
        except KeyboardInterrupt:
            break
    mot_L.disable()
    mot_R.disable()

    # Print a table of task data and a table of shared information data
    print('\n' + str(cotask.task_list))
    print(task_share.show_all())
