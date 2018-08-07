import socket, traceback
from bike_gamepad.common import Msg, prnt


class WhelMsg(Msg):
    def __init__(self, phone_value, max_value):
        self.phone_value = phone_value
        self.max_value = max_value
    @property
    def degrees(self):
        return self.phone_value * self.max_value / 9.81
    def __repr__(self):
        return '%s(%s, %s)' % (self.__class__.__name__, self.degrees, self.__dict__)


def get_wheel(max_value=255):
    host = ''
    port = 5555
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    s.bind((host, port))    
    while True:
        try:
            message, address = s.recvfrom(8192)
            yield WhelMsg(parse_msg(message)[3], max_value)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            traceback.print_exc()


def parse_msg(msg):
    #'38675.68727, 3,  -0.996,  7.815,  5.210, 5,   4.375,  0.500, 30.375'
    return [float(cell) for cell in msg.split(',')]


def main():
    for m in get_wheel():
        prnt(m)

if __name__ == '__main__':
    main()
