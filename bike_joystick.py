# Copyright (C) 2018  Joaquin Duo under GPL v3
from evdev import UInput, ecodes
from arduino_listener import yield_bike_msgs, prnt
import argparse

class VirtualJoystick(object):
    def __init__(self, max=300):
        #events = {ecodes.EV_ABS: [(ecodes.ABS_X, (0, 255, 5, 0))],}
        events = {ecodes.EV_ABS: [(ecodes.ABS_X, (-255, 255, 5, 0))],}
        self.joystick = UInput(name='virtual_bike', events=events)

    def __del__(self):
        self.joystick.close()

    def signal(self, value):
        #value = 255
        self.joystick.write(ecodes.EV_ABS, ecodes.ABS_X, value)
        self.joystick.syn()


def run_virtual_bike(args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--top', type=int, help='top rpm we think we '
                        'can make (means 100%% joystick)')
    args = parser.parse_args(args)
    vbike = VirtualJoystick()
    top_rpm = args.top
    for rpm, ratio in yield_bike_msgs(arduino_dev='/dev/ttyACM0'):
        value = int(rpm*255./top_rpm)
        prnt('rpm=%.3f ratio=%.3f', rpm, ratio)
        prnt('value=%s', value)
        vbike.signal(value)


if __name__ == '__main__':
    run_virtual_bike()
