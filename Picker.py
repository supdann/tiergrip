import time

class Tiergrip:
    def __init__(self, channel, address=0x40, frequency=60, busnum=None, init_delay=0.1):

        self.default_freq = 60
        self.pwm_scale = frequency / self.default_freq

        import Adafruit_PCA9685
        # Initialise the PCA9685 using the default address (0x40).
        if busnum is not None:
            from Adafruit_GPIO import I2C
            # replace the get_bus function with our own

            def get_bus():
                return busnum
            I2C.get_default_bus = get_bus

        self.pwm = Adafruit_PCA9685.PCA9685(address=address)
        self.pwm.set_pwm_freq(frequency)
        self.channel = channel
        time.sleep(init_delay)

    def set_pulse(self, pulse):
        self.pwm.set_pwm(self.channel, 0, int(pulse * self.pwm_scale))

    def pick(self):
        self.set_pulse(200)
        time.sleep(0.5)
        self.set_pulse(300)

    def run(self, pulse):
        self.set_pulse(pulse)
