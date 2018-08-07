# Copyright (C) 2018  Joaquin Duo under GPL v3
import serial
from bike_gamepad.common import prnt, Msg, ThreadedGenerator
try:
    from queue import Queue, Empty
except ImportError:
    from Queue import Queue, Empty


def extract_line(line):
    try:
        # First char is a flag that classifies messages (ignored)
        _, itime, litime = line.split()
        return int(itime), int(litime)
    except ValueError:
        prnt('Wrong message %r', line)
        return None


def get_bike_raw(arduino_dev):
    ser = serial.Serial(arduino_dev, 9600)
    prev_delta_t = 1
    while True:
        msg = ser.readline()
        msg = extract_line(msg)
        if msg:
            itime, litime = msg
            delta_t = itime - litime
            if delta_t < prev_delta_t:
                type_ = 'short'
            else:
                type_ = 'long'
            msg = BikeMsg(itime, litime, type_)
            yield msg
            prev_delta_t = delta_t

class BikeMsg(Msg):
    def __init__(self, itime, litime, type_):
        self.itime = itime
        self.litime = litime
        self.type = type_
    @property
    def delta(self):
        return self.itime - self.litime
    @property
    def rpm(self):
        return self.to_rpm(self.delta, type_=self.type)
    def __repr__(self):
        return '%s(%s, %s, %s)' % (self.__class__.__name__, self.rpm, self.delta, self.__dict__)
    def to_rpm(self, delta, type_='long'):
        min = 60 * 1000.
        # The long cycle is 6 times larger tha short cycle
        # So total spin time is 6 + 1 = 7
        # Proportions are:
        # - short 1/7 of the spin
        # - long 6/7 of the spin
        # We use this to conver to RPM
        if type_ == 'short':
            return min / (delta * 7)
        elif type_ == 'long':
            return min * 6 / (delta * 7)
        return 0.

class StopMsg(BikeMsg):
    def __init__(self, ):
        BikeMsg.__init__(self, itime=0, litime=0, type_='stopped')


class CalcMsg(BikeMsg):
    def __init__(self, accel=0, orig_rpm=0, attempt=1, timeout=0):
        self.accel = accel
        self.orig_rpm = orig_rpm
        self.attempt = attempt
        self.timeout = timeout # in milliseconds
    @property
    def delta(self):
        return self.attempt * self.timeout
    @property
    def rpm(self):
        if self.accel > 0:
            # Never acccelerate too much
            weight = 0.3
        else:
            # Always tend to decelerate
            weight = 0.5 * self.attempt
        return self.accel * weight * self.delta + self.orig_rpm


def get_bike_calculated(timeout=0.5, max_guess=3, arduino_dev='/dev/ttyACM0'):
    stop_msg = StopMsg()
    in_queue = Queue()
    producer = ThreadedGenerator(in_queue, get_bike_raw(arduino_dev)) 
    producer.start()
    stopped = True
    yield stop_msg
    prev_msgs = []
    attempt = 1
    while True:
        try:
            msg = in_queue.get(timeout=timeout)
            stopped = False
            attempt = 1
            yield msg
            prev_msgs.append(msg)
            if len(prev_msgs) > 10:
                prev_msgs.pop(0)
        except Empty:
            if not stopped:
                msg = extrapolate_rpm(prev_msgs, attempt, timeout * 1000)
                if attempt <= max_guess and msg.rpm > 0:
                    if attempt == 1 or msg.accel < 0:
                        yield msg
                    attempt += 1
                else:
                    stopped = True
                    attempt = 1
                    yield stop_msg


def extrapolate_rpm(prev_msgs, attempt, timeout_ms):
    if len(prev_msgs) < 2:
        return CalcMsg()
    prev, now = prev_msgs[-2:]
    prevtime = prev.litime + prev.delta / 2.
    nowtime = now.litime + now.delta / 2.
    accel = (now.rpm - prev.rpm) / float(nowtime - prevtime)
    return CalcMsg(accel, now.rpm, attempt, timeout_ms)


def main():
    for m in get_bike_calculated():
        prnt(m)


if __name__ == '__main__':
    main()
