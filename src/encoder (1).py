from pyb import Pin, Timer
import math

class Encoder:
    '''!@brief Interface with quadrature encoders
    @details Contains variables for encoder timers, position, delta, AR and PS values. Contains
    functions to return positon, delta, reset position to 0 and return speed of the motor based on 
    encoder values. 
    '''
    def __init__(self, tim_num, pin_a, pin_b, AR, PS):
        self.tim = Timer(tim_num, period = AR, prescaler = PS)
        self.enc_chan1 = self.tim.channel(1, mode = Timer.ENC_AB, pin = pin_a)
        self.enc_chan2 = self.tim.channel(2, mode = Timer.ENC_AB, pin = pin_b)
        self.AR = AR
        self.pos = 0
        self.past = 0
        self.delta = 0
        self.dradians = 0
        self.posrad = 0
        return

    def update(self):
        '''!@brief Update counter of qudrature encoders
        @details Updates the counter and adjust delta based on half of the AR Value.
        Updates the positon of the motor through delta and radians.
        @return None
        '''
    
        self.delta = self.tim.counter() - self.past
        self.past = self.tim.counter()
        if self.delta < -(self.AR+1)/2 :
            self.delta += (self.AR+1)
        if self.delta > (self.AR+1)/2 :
            self.delta -= (self.AR+1)

        self.dradians = 2 * math.pi * self.delta / 16384
        self.pos += self.delta
        self.posrad += self.dradians
        return

    def get_position(self):
        '''!@brief Gets the most recent encoder position
        @details Returns the most updated value of the encoder position
        @return float
        '''
        return self.pos

    def get_delta(self):
        '''!@brief Gets the most recent encoder delta
        @details Returns the most updated value of the delta
        @return float
        '''
        return self.delta

    def zero(self):
        '''!@brief Resets the encoder position to zero
        @details Sets the encoder position and radian position back to 0 for reset
        @return None
        '''
        self.pos = 0
        self.posrad = 0
        return 
    def get_speed(self,interval_seconds):
        '''!@brief Gets the speed of the motor
        @details Calculates the speed of the motor through the use of the seconds lapsed
        and the updated radian position
        @return float
        '''
        speed = self.dradians / interval_seconds
        return speed
