# Copyright (C) 2018  Joaquin Duo under GPL v3
from evdev import UInput, ecodes
from arduino_listener import yield_bike_msgs, prnt
import argparse
from evdev.device import AbsInfo


class VirtualJoystick(object):
    def __init__(self, top_rpm):
        cap = {1L: set([288L,
                  289L,
                  290L,
                  291L,
                  292L,
                  293L,
                  294L,
                  295L,
                  296L,
                  297L,
                  298L,
                  299L]),
         3L: set([(0,
                   AbsInfo(value=top_rpm, min=0, max=top_rpm*2, fuzz=0, flat=15, resolution=0)),
                  (1L,
                   AbsInfo(value=128, min=0, max=255, fuzz=0, flat=15, resolution=0)),
                  (2L,
                   AbsInfo(value=134, min=0, max=255, fuzz=0, flat=15, resolution=0)),
                  (3L,
                   AbsInfo(value=128, min=0, max=255, fuzz=0, flat=15, resolution=0)),
                  (4L,
                   AbsInfo(value=128, min=0, max=255, fuzz=0, flat=15, resolution=0)),
                  (16L,
                   AbsInfo(value=0, min=-1, max=1, fuzz=0, flat=0, resolution=0)),
                  (17L,
                   AbsInfo(value=0, min=-1, max=1, fuzz=0, flat=0, resolution=0))]),
         4L: set([4L])}
        self.joystick = UInput(cap, name='gpad-bike')

    def __del__(self):
        self.joystick.close()

    def signal(self, value):
        #value = 255
        self.joystick.write(ecodes.EV_ABS, ecodes.ABS_X, value)
        self.joystick.syn()


def run_virtual_bike(args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--top', type=int, default=714,
                        help='top rpm we think we '
                        'can make (means 100%% joystick)')
    args = parser.parse_args(args)
    vbike = VirtualJoystick(args.top)
    max_measure = 0
    for msg in yield_bike_msgs(arduino_dev='/dev/ttyACM0'):
        rpm = msg.rpm
        if not rpm:
            max_measure = 0
        max_measure = max(rpm, max_measure)
        value = int(rpm + args.top)
        prnt('value=%s, rpm=%.3f, top=%s', value, rpm, max_measure)
        vbike.signal(value)


if __name__ == '__main__':
    run_virtual_bike()
