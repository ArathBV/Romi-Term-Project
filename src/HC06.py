from pyb import Pin, Timer, UART
import pyb
'''
!@brief HC06-RS232 Driver Class for Serial Bluetooth Communication
Driver uses USART3 on the STM32L476RG Board and establishes a REPL
connection to be displayed through the Serial
'''
class HC06 :
    def __init__(self):
        # USART 3 on STM32 PC5 TX and PC10 RX
        self.uart = UART(3, 9600)
        self.tx = Pin(Pin.cpu.C5, mode=Pin.ALT, alt=7)
        self.rx = Pin(Pin.cpu.C10, mode=Pin.ALT, alt=7)
        return 
        
    def writeData(self, data):
        '''
        !@brief Allows for data to be written to the Serial Connection
        '''
        self.uart.write(data)
        return

    def estREPL(self):
        '''
        !@brief Establishes a REPL connection through the Serial
        '''
        pyb.repl_uart(self.uart)
        return
