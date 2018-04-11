# Copyright (C) 2018  Joaquin Duo under GPL v3
import serial
import threading
try:
    from queue import Queue, Empty
except ImportError:
    from Queue import Queue, Empty

def to_rpm(itime, litime):
    # Alsways assume 1 spin in the delta time
    # Arduino is fast enough to count 1 spin and send the message
    return 60000 / float(itime - litime)

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
        delta_ratio = 0.01
        while True:
            msg = ser.readline()
            msg = extract_line(msg)
            if msg:
                itime, litime = msg
                delta_t = itime - litime
                if delta_t < prev_delta_t:
                    # Its a small ON cycle
                    delta_ratio = delta_t / float(prev_delta_t)
                else:
                    # Its a large OFF cycle (full spin) 
                    rpm = to_rpm(itime, litime)
                    self.msg_queue.put((rpm, delta_ratio))
                prev_delta_t = delta_t


def yield_bike_msgs(timeout=1.5, arduino_dev='/dev/ttyACM0'):
    stopped_msg = (0, 1.)
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
