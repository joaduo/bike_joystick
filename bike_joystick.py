# Copyright (C) 2018  Joaquin Duo under GPL v3
from evdev import UInput, ecodes
from arduino_listener import yield_bike_msgs, prnt

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


def run_virtual_bike(max=300):
    vbike = VirtualJoystick()
    for rpm, ratio in yield_bike_msgs(arduino_dev='/dev/ttyACM0'):
        value = int(rpm*255./300.)
        prnt('rpm=%.3f ratio=%.3f', rpm, ratio)
        prnt('value=%s', value)
        vbike.signal(value)


if __name__ == '__main__':
    run_virtual_bike()
