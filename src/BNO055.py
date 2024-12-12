from pyb import I2C
from pyb import Pin

'''
BNO-MCU Pin Layout
# SDA - PB11
# SCL = PB10
# RESET = GND
# Vdd = 3.3V
# GND = GND
'''

# BNO Addresses
BNO_ADDR = 0x28
BNO_CONFIG_MODE = 0x00
BNO_NDOF_MODE = 0x0C
BNO_OPR_MODE = 0x3D
BNO_PWR_ADDR = 0x3E
BNO_CALIB_ADDR = 0x35
BNO_UNITSEL_ADDR = 0x80
BNO_CALIB_COEF_ADDR = 0x55

# Gryoscope Addresses
GYR_ADDR_0 = 0x0A
GYR_ADDR_1 = 0x0B
GYR_X_LSB = 0x14
GYR_X_MSB = 0x15
GYR_Y_LSB = 0x16
GYR_Y_MSB = 0x17
GYR_Z_LSB = 0x18
GYR_Z_MSB = 0x19

# Accelerometer Addresses
ACCL_ADDR_Config = 0x08
ACCL_X_LSB = 0x08
ACCL_X_MSB = 0x09
ACCL_Y_LSB = 0x0A
ACCL_Y_MSB = 0x0B
ACCL_Z_LSB = 0x0C
ACCL_Z_MSB = 0x0D

# Euler Address
EUL_X_LSB = 0x1A
EUL_X_MSB = 0x1B
EUL_Y_LSB = 0x1C
EUL_Y_MSB = 0x1D
EUL_Z_LSB = 0x1E
EUL_Z_MSB = 0x1F


class BNO055:
    '''
    !@brief BNO055 IMU Driver Class that uses I2C with the STM32L476RG Board 
    Contains the Configurations for the IMU in Normal Mode and Fusion Mode. 
    Contains Functions to configure the Accelrometer, Gyroscope, and 
    Magnometer. Driver allows for the IMU status, Euler Angles, Yaw, and 
    Calibration Coefficient.
    '''
    def __init__(self):
        '''
        !@brief Initializes the BNO055 I2C configuration and address
        '''
        self.i2c = I2C(2, I2C.CONTROLLER, baudrate=400000)
        self.addr = BNO_ADDR
        self.eulX = None
        self.eulY = None
        self.eulZ = None
        return

    def imuConfig(self):
        '''
        !@brief IMU Configured to Fusion Mode
        !@details IMU is sent the data of entering Fusion Mode 
        to the Operation Mode Register
        !@return None
        '''
        self.i2c.mem_write(BNO_NDOF_MODE, self.addr, BNO_OPR_MODE)
        return

    def gyroConfig(self):
        '''
        !@brief Configures the Gyroscope of the IMU
        !@details Writes the mode to the gyroscope 1 register.
        Writes to specified Bandwidth and Range selection of the
        gyroscope data to the gyroscope 2 register
        !@return None
        '''
        # Power Mode
        self.i2c.mem_write(0x00, self.addr, GYR_ADDR_1)
        data_config = (0x00) | ((0x02) << 3)
        self.i2c.mem_write(data_config, self.addr, GYR_ADDR_0)
        return

    def accelConfig(self):
        '''
        !@brief Configures the Accelerometer of the IMU
        !@details Writes the Range, Bandwidth, and Mode of the
        accelerometer to the configuration address
        !@return None
        '''
        data_config = (0x02) | (0x04 << 2) | (0x00 << 5)
        self.i2c.mem_write(data_config, self.addr, ACCL_ADDR_Config)
        return

    def fusionConfig(self):
        '''
        !@brief Configures Fusion Mode
        !@details Writes to the Fusion Mode address setting the readings
        to nine degrees of freedom and setting the Euler Readings to Radians
        !@return None
        '''
        self.i2c.mem_write(0x00, self.addr, BNO_NDOF_MODE)  
        self.i2c.mem_write(0x04, self.addr, BNO_UNITSEL_ADDR)  
        return

    def readCalibrationStatus(self):
        '''
        !@brief Reads the Calibration Status of the IMU
        !@details Reads the first byte of information of the system's calibration
        status. Bit shifts the data depending on the configuration of each measurement
        unit and the system. Prints out the status of each unit and system.
        !@return None
        ''' 
        calib_status = self.i2c.mem_read(1, self.addr, BNO_CALIB_ADDR)[0]
        sys = (calib_status >> 6) & 0x03
        gyro = (calib_status >> 4) & 0x03
        accel = (calib_status >> 2) & 0x03
        mag = (calib_status) & 0x03
        print(f"System status: {sys}, Gyro status: {gyro}, Accel status: {accel}, Mag status: {mag}")
        return

    def readCalibrationCoeff(self):
        '''
        !@brief Reads the Calibration Coefficient of the IMU
        !@details Reads the 22 bytes of data of the system's calibration coefficient, starting
        from the Calibration Coefficient Address.
        !@return bytearray
        ''' 
        return self.i2c.mem_read(22, self.addr, BNO_CALIB_COEF_ADDR)

    def writeCalibrationCoeff(self, data):
        '''
        !@brief Writes the Calibration Status of the IMU
        !@details Writes a byte array (22 Bytes of data) to the Calibration
        Coefficient Registers
        !@return None
        ''' 
        self.i2c.mem_write(data, self.addr, BNO_CALIB_COEF_ADDR)
        return

    def readEuler(self):
        '''
        !@brief Reads the Euler Angles of the IMU
        !@details Reads the 6 bytes of data from the first address of the LSB of the EULER
        registers. Each 16 bit number is then converted to a signed integer and updates the
        class Euler variables.
        !@return None
        ''' 
        euler_data = self.i2c.mem_read(6, self.addr, EUL_X_LSB)
        self.eulX = int.from_bytes(euler_data[0:2], 'little', True)
        self.eulY = int.from_bytes(euler_data[2:4], 'little', True)
        self.eulZ = int.from_bytes(euler_data[4:6], 'little', True)
        return

    def getEulX(self):
        '''
        !@brief Gets the Euler X data
        !@return int
        '''
        if(self.eulX >= 32768):
            return (self.eulX - 65536)/900
        return self.eulX /900

    def getEulY(self):
        '''
        !@brief Gets the Euler Y data
        !@return int
        '''
        if(self.eulY >= 32768):
            return (self.eulY - 65536)/900
        return self.eulY /900

    def getEulZ(self):
        '''
        !@brief Gets the Euler Z data
        !@return int
        '''
        if(self.eulZ >= 32768):
            return (self.eulZ - 65536)/900
        return self.eulZ /900

    def readYaw(self):
        '''
        !@brief Reads the Gyroscope Measurment on the Z axis
        !@details Reads 2 bytes of data from the LSB of the Z register to
        get the full Z Gyroscope reading. The data is then converted to a signed
        integer which is subtracted by half of the full scale reading and then 
        divided by 900 due to the measurement reading resolution 
        and being in radians.
        !@return int
        '''
        gyrZdata = self.i2c.mem_read(2, self.addr, GYR_Z_LSB)
        yaw = int.from_bytes(gyrZdata, 'little', True)
        if(yaw >= 32768):
            yaw -= 65536
        return yaw/900
