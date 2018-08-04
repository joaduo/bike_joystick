# Copyright (C) 2018  Joaquin Duo under GPL v3
import serial
import threading
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

def prnt(msg, *args):
    if args:
        msg = msg % args
    print(msg)

class ArduinoBikeListener(threading.Thread):
    def __init__(self, arduino_dev, msg_queue, group=None, target=None, name=None, 
        args=(), kwargs=None, verbose=None):
        threading.Thread.__init__(self, group=group, target=target, name=name,
                                  args=args, kwargs=kwargs, verbose=verbose)
        self.msg_queue = msg_queue
        self.arduino_dev = arduino_dev

    def run(self):
        ser = serial.Serial(self.arduino_dev, 9600)
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
                self.msg_queue.put(msg)
                prev_delta_t = delta_t


class BikeMsg(object):
    def __init__(self, itime=0, litime=0, type_='stopped'):
        self.itime = itime
        self.litime = litime
        self.type = type_

    @property
    def delta(self):
        return self.itime - self.litime

    @property
    def rpm(self):
        min = 60 * 1000.
        # The long cycle is 6 times larger tha short cycle
        # So total spin time is 6 + 1 = 7
        # Proportions are:
        # - short 1/7 of the spin
        # - long 6/7 of the spin
        # We use this to conver to RPM
        if self.type == 'short':
            return min / (self.delta * 7)
        elif self.type == 'long':
            return min * 6 / (self.delta * 7)
        return 0.


def yield_bike_msgs(timeout=1.5, arduino_dev='/dev/ttyACM0'):
    stopped_msg = BikeMsg()
    msg_queue = Queue()
    listener = ArduinoBikeListener(arduino_dev, msg_queue)
    listener.start()
    stopped = True
    yield stopped_msg
    while True:
        try:
            msg = msg_queue.get(timeout=timeout)
            stopped = False
            yield msg
        except Empty:
            if not stopped:
                stopped = True
                yield stopped_msg 

def main():
    for m in yield_bike_msgs():
        #prnt(m)
        rpm, ratio = m
        prnt('%.2f%% %.2f %s.2f', rpm * 100 /300., rpm, ratio)


if __name__ == '__main__':
    main()
