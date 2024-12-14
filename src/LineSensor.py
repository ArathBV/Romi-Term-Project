from pyb import Pin, Timer
from time import sleep_us, ticks_us, ticks_diff

# Vcc = 5V
# GND = GND
# LED_ON = 5V
from array import array

def black_or_white(value):
    '''!@brief Normalizing the light sensor readings at specific cutoff threshold
    !@param int
    !@return int
    '''
    if value >= 4000:
        return 1
    else:
        return 0

class LineSensor:
    '''!@brief Line Sensor Driver Class for the QT8-RC Array Sensor.
    Driver contains Configuration for the Line Sensor Pins, reading functions with and without 
    threshold values for testing purposes, printing statements which update before or retrieve last readings, and 
    weighted centroid function for speed adjustments.
    '''
    def __init__(self):
        '''
        !@brief Initializes Line Sensor RC pins and sensor reading arrays
        '''
        # Sensor Pins
        self.s1 = None
        self.s2 = None
        self.s3 = None
        self.s4 = None
        self.s5 = None
        self.s6 = None
        self.s7 = None
        self.s8 = None
        self.sensors = [0, 0, 0, 0, 0, 0, 0, 0]
        self.sens_array = array("f", (0, 0, 0, 0, 0, 0, 0, 0))
        self.small_array = array("f", (0, 0))

    def sensConfig(self, s1, s2, s3, s4, s5, s6, s7, s8):
        '''
        !@brief Configuration Function that sets up each I/O pin on the Line Sensor
        !@param Pin Name i.e Pin.cpu.PX#
        !@return None
        '''
        self.s1 = Pin(s1, mode=Pin.OUT_PP)
        self.s2 = Pin(s2, mode=Pin.OUT_PP)
        self.s3 = Pin(s3, mode=Pin.OUT_PP)
        self.s4 = Pin(s4, mode=Pin.OUT_PP)
        self.s5 = Pin(s5, mode=Pin.OUT_PP)
        self.s6 = Pin(s6, mode=Pin.OUT_PP)
        self.s7 = Pin(s7, mode=Pin.OUT_PP)
        self.s8 = Pin(s8, mode=Pin.OUT_PP)
        return

    def readSensor(self, pin):
        '''
        !@brief Read Sensor Function that sets the I/O pin high for 10us if the pin is configured. Once the
        pin is set to high it is reconfigured as an input pin. A ticks timer object is started 
        to measure the time for the capacitor to discharge. Function is used for tuning and gathering data on
        each sensor. 
        !@param pyb.Pin
        !@return int
        '''
        if pin == None:
            return -100
        pin.init(mode=Pin.OUT_PP)
        pin.high()
        sleep_us(10)

        pin.init(mode=Pin.IN)
        start_time = ticks_us()

        while pin.value() == 1:
            continue

        elapsed_time = ticks_diff(ticks_us(), start_time)
        return elapsed_time

    def readSensor2(self, pin):
        '''
        !@brief Read Sensor 2 Function sets the I/O pin high for 10us if the pin is configured. Once the
        pin is set to high it is reconfigured as an input pin. A ticks timer object is started 
        to measure the time for the capacitor to discharge until a threshold is reached to ensure quick and accurate data. 
        Function is used for determining white or dark surface. 
        !@param pyb.Pin
        !@return int
        '''
        if pin == None:
            return -100
        pin.init(mode=Pin.OUT_PP)
        pin.high()
        sleep_us(10)

        pin.init(mode=Pin.IN)
        start_time = ticks_us()

        while pin.value() == 1:
            if ticks_diff(ticks_us(), start_time) >= 5000:
                break
            continue

        elapsed_time = ticks_diff(ticks_us(), start_time)
        print(elapsed_time)
        return elapsed_time

    def printSensorReadings(self):
        '''
        !@brief Function that updates and gets the current sensor readings which are then printed out in 
        a table format
        !@return None
        '''
        self.sensors[0] = self.readSensor(self.s1)
        self.sensors[1] = self.readSensor(self.s2)
        self.sensors[2] = self.readSensor(self.s3)
        self.sensors[3] = self.readSensor(self.s4)
        self.sensors[4] = self.readSensor(self.s5)
        self.sensors[5] = self.readSensor(self.s6)
        self.sensors[6] = self.readSensor(self.s7)
        self.sensors[7] = self.readSensor(self.s8)

        print("|   s1   |   s2   |   s3   |   s4   |   s5   |   s6   |   s7   |   s8   |")
        print(chr(0xAF) * 75)
        print(f"|   {self.sensors[0]}   |   {self.sensors[1]}   |   {self.sensors[2]}   |   \
{self.sensors[3]}   |   {self.sensors[4]}   |   {self.sensors[5]}   |   {self.sensors[6]}   |   {self.sensors[7]}   |")
        return None

    def printSensValues(self):
        '''
        !@brief Function that gets the last updated sensor readings which are then printed out in 
        a table format
        !@return None
        '''
        print("|   s1   |   s2   |   s3   |   s4   |   s5   |   s6   |   s7   |   s8   |")
        print(chr(0xAF) * 75)
        print(f"|   {self.sensors[0]}   |   {self.sensors[1]}   |   {self.sensors[2]}   |   {self.sensors[3]}   |   \
{self.sensors[4]}   |   {self.sensors[5]}   |   {self.sensors[6]}   |   {self.sensors[7]}   |")
        return None

    def centroid3(self):
        '''
        !@brief Centroid function helps determine which sensors are detecting the line. Gathers the data from each 
        sensor using the black or white threshold function. Depending on which values sense the line, the centroid is update
        from positive meaning turn right, and negative turn left, and 1 being in the center. If all sensors detect the line, 
        a straight line flag is raised for FSM Romi Tasks Purposes.
        !@return tuple
        '''
        self.sens_array[0] = black_or_white(self.readSensor2(self.s1))
        self.sens_array[1] = black_or_white(self.readSensor2(self.s2))
        self.sens_array[2] = black_or_white(self.readSensor2(self.s3))
        self.sens_array[3] = black_or_white(self.readSensor2(self.s4))
        self.sens_array[4] = black_or_white(self.readSensor2(self.s5))
        self.sens_array[5] = black_or_white(self.readSensor2(self.s6))
        self.sens_array[6] = black_or_white(self.readSensor2(self.s7))
        self.sens_array[7] = black_or_white(self.readSensor2(self.s8))
        centroid = 0
        line = 0

        centroid += (self.sens_array[0]*15 + self.sens_array[1]*8 + self.sens_array[2]*4 + self.sens_array[3]*1 +
                     self.sens_array[4]*-1 + self.sens_array[5]*-4 + self.sens_array[6]*-8 +self.sens_array[7]*-15)
        # Check for crossing a solid line (far sensors both read black):
        if self.sens_array[0] and self.sens_array[7]:
            line = 1
        return centroid, line
