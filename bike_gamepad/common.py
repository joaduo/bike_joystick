# Copyright (C) 2018  Joaquin Duo under GPL v3
import threading


def prnt(msg, *args):
    if args:
        msg = msg % args
    print(msg)


class Msg(object):
    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, self.__dict__)


class ThreadedGenerator(threading.Thread):
    def __init__(self, out_queue, generator, group=None, name=None, verbose=None):
        threading.Thread.__init__(self, group=group, name=name, verbose=verbose)
        self._out_queue = out_queue
        self._generator = generator

    def run(self):
        for msg in self._generator:
            self._out_queue.put(msg)

