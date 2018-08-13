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

    def write(self, etype, code, value):
        self.joystick.write(etype, code, value)


class ThresholdKey(object):
    def __init__(self, threshold, key_code, uinput):
        self.threshold = threshold
        self.key_code = key_code
        self.uinput = uinput
        self._pressed = 0

    def set_key(self, value):
        if value != self._pressed:
            logger.debug('%s: Setting %s to %s', self.__class__.__name__, self.key_code, value)
            self._pressed = value
            self.uinput.write(ecodes.EV_KEY, self.key_code, self._pressed)

    def process(self, value):
        if not self.threshold:
            return
        if self.threshold < abs(value):
            self.set_key(1)
        else:
            self.set_key(0)


def run_virtual_bike(args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--rpm-threshold', type=float, default=200,
                        help='Rpm that makes full axis')
    parser.add_argument('--rpm-top', type=float, default=660,
                        help='RPM axis top (default=660)')
    parser.add_argument('--rpm-button', type=float, default=None,
                        help='Threhold to activate button')
    parser.add_argument('--wheel-threshold', type=float, default=60,
                        help='Degree that makes full axis (default=60)')
    parser.add_argument('--wheel-top', type=float, default=256,
                        help='Wheel axis top (default=256)')
    parser.add_argument('--wheel-button', type=float, default=None,
                        help='Degree threshold to activate button')
    parser.add_argument('-D', '--debug', action='store_true',
                        help='show debug msgs')
    args = parser.parse_args(args)
    logging.basicConfig()
    if args.debug:
        logger.setLevel(logging.DEBUG)
    wheel_top = args.wheel_top #arbitrary number (to give enough gradient)
    rpm_top = args.rpm_top #my physical limit
    vbike = VirtualJoystick(rpm_top, wheel_top)
    msgs = Queue()
    bike = ThreadedGenerator(msgs, get_bike_calculated())
    bike.start()
    wheel = ThreadedGenerator(msgs, get_wheel(wheel_top))
    wheel.start()
    wheelkey = ThresholdKey(args.wheel_button, ecodes.BTN_THUMB, vbike)
    rpmkey = ThresholdKey(args.rpm_button * wheel_top/90., ecodes.BTN_THUMB2, vbike)
    while True:
        msg = msgs.get()
        if isinstance(msg, BikeMsg):
            vbike.set_rpm(int(msg.rpm * float(rpm_top)/args.rpm_threshold) + rpm_top)
            rpmkey.process(msg.rpm)
        elif isinstance(msg, WhelMsg):
            # wheel threshols is in degrees, max is 90 degrees
            vbike.set_wheel(int(msg.degrees * 90./args.wheel_threshold) + wheel_top)
            wheelkey.process(msg.degrees)
        logger.debug(msg)


if __name__ == '__main__':
    run_virtual_bike()
