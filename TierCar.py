#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
from statistics import median
from threading import Thread

# from .memory import Memory


class PCA9685:
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
        # "Tamiya TBLE-02" makes a little leap otherwise
        time.sleep(init_delay)

    def set_pulse(self, pulse):
        self.pwm.set_pwm(self.channel, 0, int(pulse * self.pwm_scale))

    def run(self, pulse):
        self.set_pulse(pulse)


class TierCar:

    def __init__(self, mem=None):

        # if not mem:
        #     mem = Memory()
        # self.mem = mem
        self.parts = []
        self.on = True
        self.threads = []
        self.throttle = PCA9685(0)
        self.steering = PCA9685(1)

    def moveForward(self):
        self.throttle.set_pulse(455)
        time.sleep(1)
        self.steering.set_pulse(410)

    def add(self, part, inputs=[], outputs=[], threaded=False, run_condition=None):

        assert type(inputs) is list, "inputs is not a list: %r" % inputs
        assert type(outputs) is list, "outputs is not a list: %r" % outputs
        assert type(
            threaded) is bool, "threaded is not a boolean: %r" % threaded

        p = part
        print('Adding part {}.'.format(p.__class__.__name__))
        entry = {}
        entry['part'] = p
        entry['inputs'] = inputs
        entry['outputs'] = outputs
        entry['run_condition'] = run_condition

        if threaded:
            t = Thread(target=part.update, args=())
            t.daemon = True
            entry['thread'] = t

        self.parts.append(entry)
        # self.profiler.profile_part(part)

    def start(self, rate_hz=10, max_loop_count=None, verbose=False):

        try:

            self.on = True

            for entry in self.parts:
                if entry.get('thread'):
                    # start the update thread
                    entry.get('thread').start()

            # wait until the parts warm up.
            print('Starting vehicle...')
            # time.sleep(1)

            loop_count = 0
            while self.on:
                start_time = time.time()
                loop_count += 1

                self.update_parts()

                # stop drive loop if loop_count exceeds max_loopcount
                if max_loop_count and loop_count > max_loop_count:
                    self.on = False

                sleep_time = 1.0 / rate_hz - (time.time() - start_time)
                if sleep_time > 0.0:
                    time.sleep(sleep_time)
                else:
                    # print a message when could not maintain loop rate.
                    if verbose:
                        print(
                            'WARN::Vehicle: jitter violation in vehicle loop with value:', abs(sleep_time))

                # if verbose and loop_count % 200 == 0:
                #     self.profiler.report()

        except KeyboardInterrupt:
            pass
        finally:
            self.stop()

    def update_parts(self):
        '''
        loop over all parts
        '''
        for entry in self.parts:

            run = True

            # # check run condition, if it exists
            # if entry.get('run_condition'):
            #     run_condition = entry.get('run_condition')
            #     run = self.mem.get([run_condition])[0]

            # if run:
            #     # get part
            #     p = entry['part']

            #     # start timing part run
            #     self.profiler.on_part_start(p)

            #     # get inputs from memory
            #     inputs = self.mem.get(entry['inputs'])

            #     # run the part
            #     if entry.get('thread'):
            #         outputs = p.run_threaded(*inputs)
            #     else:
            #         outputs = p.run(*inputs)

            #     # save the output to memory
            #     if outputs is not None:
            #         self.mem.put(entry['outputs'], outputs)

            #     # finish timing part run
            #     self.profiler.on_part_finished(p)

    def stop(self):
        print('Shutting down vehicle and its parts...')
        for entry in self.parts:
            try:
                entry['part'].shutdown()
            except AttributeError:
                # usually from missing shutdown method, which should be optional
                pass
            except Exception as e:
                print(e)


if __name__ == '__main__':

    tierCar = TierCar()
    tierCar.moveForward()
