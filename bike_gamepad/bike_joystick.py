# Copyright (C) 2018  Joaquin Duo under GPL v3
from evdev import UInput, ecodes
from bike_gamepad.rpm_listener import get_bike_calculated, prnt, BikeMsg
import argparse
from evdev.device import AbsInfo
from bike_gamepad.common import ThreadedGenerator
from bike_gamepad.wheel_listener import get_wheel, WhelMsg
import logging
try:
    from queue import Queue, Empty
except ImportError:
    from Queue import Queue, Empty


logger = logging.getLogger(__name__)

class VirtualJoystick(object):
    def __init__(self, top_rpm, top_wheel):
        e = ecodes
        cap = {
                e.EV_ABS: [  (e.ABS_X,
                              AbsInfo(value=top_wheel, min=0, max=top_wheel*2, fuzz=0, flat=15, resolution=0)),
                             (e.ABS_Y,
                              AbsInfo(value=128, min=0, max=255, fuzz=0, flat=15, resolution=0)),
                             (e.ABS_Z,
                              AbsInfo(value=top_rpm, min=0, max=top_rpm*2, fuzz=0, flat=15, resolution=0)),
                             ],
                e.EV_KEY: [e.BTN_JOYSTICK,
                            e.BTN_THUMB,
                            e.BTN_THUMB2,
                            e.BTN_TOP,
                            e.BTN_TOP2,
                            e.BTN_PINKIE,
                            e.BTN_BASE,
                            e.BTN_BASE2,
                            e.BTN_BASE3,
                            e.BTN_BASE4,
                            e.BTN_BASE5,
                            e.BTN_BASE6],
               }
        self.joystick = UInput(cap, name='gpad-bike')

    def __del__(self):
        self.joystick.close()

    def set_wheel(self, value):
        self.set_axis(ecodes.ABS_X, value)

    def set_rpm(self, value):
        self.set_axis(ecodes.ABS_Z, value)

    def set_axis(self, axis, value):
        #value = 255
        self.joystick.write(ecodes.EV_ABS, axis, value)
        self.joystick.syn()


def run_virtual_bike(args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--rpm-mult', type=float, default=1.,
                        help='rpm multiplier')
    parser.add_argument('--rpm-top', type=float, default=660,
                        help='Top rpm user can do')
    parser.add_argument('--rpm-button', type=float, default=None,
                        help='Threhold to activate button')
    parser.add_argument('-w', '--wheel-mult', type=float, default=1.,
                        help='wheel degree multiplier')
    parser.add_argument('--wheel-top', type=float, default=256,
                        help='Top number at 90 degrees')
    parser.add_argument('--wheel-button', type=float, default=None,
                        help='Threhold to activate button')
    parser.add_argument('-D', '--debug', action='store_true',
                        help='show debug msgs')
    args = parser.parse_args(args)
    logging.basicConfig()
    if args.debug:
        logger.setLevel(logging.DEBUG)
    top_degrees = args.wheel_top #arbitrary number (to give enough gradient)
    top_rpm = args.rpm_top #my physical limit
    vbike = VirtualJoystick(top_rpm, top_degrees)
    msgs = Queue()
    bike = ThreadedGenerator(msgs, get_bike_calculated())
    bike.start()
    wheel = ThreadedGenerator(msgs, get_wheel(top_degrees))
    wheel.start()
    while True:
        msg = msgs.get()
        if isinstance(msg, BikeMsg):
            vbike.set_rpm(int(msg.rpm * args.rpm_mult) + top_rpm)
        elif isinstance(msg, WhelMsg):
            vbike.set_wheel(int(msg.degrees * args.wheel_mult) + top_degrees)
        logger.debug(msg)


if __name__ == '__main__':
    run_virtual_bike()
