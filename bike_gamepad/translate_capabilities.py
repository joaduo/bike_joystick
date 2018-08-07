from evdev.device import AbsInfo
from pprint import pformat
import re

def examples():
    real_cap = {1L: set([288L,
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
                       AbsInfo(value=128, min=0, max=255, fuzz=0, flat=15, resolution=0)),
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
    
    verbose_cap = {('EV_ABS', 3L): [(('ABS_X', 0),
                              AbsInfo(value=128, min=0, max=255, fuzz=0, flat=15, resolution=0)),
                             (('ABS_Y', 1L),
                              AbsInfo(value=128, min=0, max=255, fuzz=0, flat=15, resolution=0)),
                             (('ABS_Z', 2L),
                              AbsInfo(value=134, min=0, max=255, fuzz=0, flat=15, resolution=0)),
                             (('ABS_RX', 3L),
                              AbsInfo(value=128, min=0, max=255, fuzz=0, flat=15, resolution=0)),
                             (('ABS_RY', 4L),
                              AbsInfo(value=128, min=0, max=255, fuzz=0, flat=15, resolution=0)),
                             (('ABS_HAT0X', 16L),
                              AbsInfo(value=0, min=-1, max=1, fuzz=0, flat=0, resolution=0)),
                             (('ABS_HAT0Y', 17L),
                              AbsInfo(value=0, min=-1, max=1, fuzz=0, flat=0, resolution=0))],
            ('EV_FF', 21L): [(['FF_EFFECT_MIN', 'FF_RUMBLE'], 80L),
                             ('FF_PERIODIC', 81L),
                             (['FF_SQUARE', 'FF_WAVEFORM_MIN'], 88L),
                             ('FF_TRIANGLE', 89L),
                             ('FF_SINE', 90L),
                             (['FF_GAIN', 'FF_MAX_EFFECTS'], 96L)],
            ('EV_KEY', 1L): [(['BTN_JOYSTICK', 'BTN_TRIGGER'], 288L),
                             ('BTN_THUMB', 289L),
                             ('BTN_THUMB2', 290L),
                             ('BTN_TOP', 291L),
                             ('BTN_TOP2', 292L),
                             ('BTN_PINKIE', 293L),
                             ('BTN_BASE', 294L),
                             ('BTN_BASE2', 295L),
                             ('BTN_BASE3', 296L),
                             ('BTN_BASE4', 297L),
                             ('BTN_BASE5', 298L),
                             ('BTN_BASE6', 299L)],
            ('EV_MSC', 4L): [('MSC_SCAN', 4L)],
            ('EV_SYN', 0): [('SYN_REPORT', 0),
                             ('SYN_CONFIG', 1L),
                             ('SYN_DROPPED', 3L),
                             ('?', 4L),
                             ('?', 21L)]}
    pformat_str = '''
{'EV_ABS': [('ABS_X',
             AbsInfo(value=128, min=0, max=255, fuzz=0, flat=15, resolution=0)),
            ('ABS_Y',
             AbsInfo(value=128, min=0, max=255, fuzz=0, flat=15, resolution=0)),
            ('ABS_Z',
             AbsInfo(value=134, min=0, max=255, fuzz=0, flat=15, resolution=0)),
            ('ABS_RX',
             AbsInfo(value=128, min=0, max=255, fuzz=0, flat=15, resolution=0)),
            ('ABS_RY',
             AbsInfo(value=128, min=0, max=255, fuzz=0, flat=15, resolution=0)),
            ('ABS_HAT0X',
             AbsInfo(value=0, min=-1, max=1, fuzz=0, flat=0, resolution=0)),
            ('ABS_HAT0Y',
             AbsInfo(value=0, min=-1, max=1, fuzz=0, flat=0, resolution=0))],
 'EV_FF': ['FF_EFFECT_MIN',
           'FF_PERIODIC',
           'FF_SQUARE',
           'FF_TRIANGLE',
           'FF_SINE',
           'FF_GAIN'],
 'EV_KEY': ['BTN_JOYSTICK',
            'BTN_THUMB',
            'BTN_THUMB2',
            'BTN_TOP',
            'BTN_TOP2',
            'BTN_PINKIE',
            'BTN_BASE',
            'BTN_BASE2',
            'BTN_BASE3',
            'BTN_BASE4',
            'BTN_BASE5',
            'BTN_BASE6'],
 'EV_MSC': ['MSC_SCAN'],
 'EV_SYN': ['SYN_REPORT', 'SYN_CONFIG', 'SYN_DROPPED', 4, 21]}
'''
    return real_cap, verbose_cap, pformat_str


def _get_new_key(k):
    if len(k) >1 and isinstance(k[1], AbsInfo):
        return (_get_new_key(k[0]), k[1])
    if k[0] == '?':
        return int(k[1])
    if isinstance(k[0], list):
        return k[0][0]
    return k[0]


def _translate_verbose_cap(cap, clean=True):
    new_cap = {}
    for k,v in cap.items():
        if isinstance(v, list):
            v =  [_get_new_key(el) for el in v]
        k = _get_new_key(k)
        if clean and isinstance(k, str) and ('FF' in k or 'SYN' in k):
            continue
        new_cap[k] = v
    return new_cap


def _replace_strings_with_code(pformat):
    return re.sub(r"'([A-Z0-9_]+)'", r'e.\1', pformat)


def evdev_verbose_capabilities_to_code_sting(cap):
    cap = _translate_verbose_cap(cap)
    return _replace_strings_with_code(pformat(cap))


if __name__ == '__main__':
    cap = examples()[1]
    print(evdev_verbose_capabilities_to_code_sting(cap))

