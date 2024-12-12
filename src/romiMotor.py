from pyb import Pin, Timer

class RomiMotor:
    '''!@brief A driver class for one channel of the L6206.
    @details Objects of this class can be used to apply PWM to a given
    DC motor on one channel of the L6206 from ST Microelectronics.
        '''
    def __init__(self, pwm_tim, pwm_pin, dir_pin, en_pin):
        '''!@brief Initializes and returns an object associated with a DC motor.
        '''
        self.pwm_pin = Pin(pwm_pin, mode=Pin.OUT_PP)
        self.dir_pin = Pin(dir_pin, mode=Pin.OUT_PP)
        self.en_pin = Pin(en_pin, mode=Pin.OUT_PP)
        #self.PWM_CH1 = pwm_tim.channel(1, mode=Timer.PWM, pin=self.IN1pin)
        #self.PWM_CH2 = pwm_tim.channel(2, mode=Timer.PWM, pin=self.IN2pin)
        self.pwm_ch1 = pwm_tim.channel(1, mode=Timer.PWM, pin=self.pwm_pin)
        return

    def set_duty(self, duty):
        '''!@brief Set the PWM duty cycle for the DC motor.
        @details This method sets the duty cycle to be sent
        to the L6206 to a given level. Positive values
        cause effort in one direction, negative values
        in the opposite direction.
        @param duty A signed number holding the duty
        cycle of the PWM signal sent to the L6206
        '''
        if (duty < 0):
            self.dir_pin.high()
            self.pwm_ch1.pulse_width_percent(abs(duty))
            #self.PWM_CH1.pulse_width_percent(abs(duty))
            #self.PWM_CH2.pulse_width_percent(0)
        else:
            self.dir_pin.low()
            self.pwm_ch1.pulse_width_percent(duty)
            #self.PWM_CH2.pulse_width_percent(duty)
            #self.PWM_CH1.pulse_width_percent(0)
        return

    def enable(self):
        '''!@brief Enable one channel of the L6206.
        @details This method sets the enable pin associated with one
        channel of the L6206 high in order to enable that
        channel of the motor driver.
        '''
        self.en_pin.high()
        return

    def disable(self):
        self.en_pin.low()
        return
