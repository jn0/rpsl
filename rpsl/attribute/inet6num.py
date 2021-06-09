#!python3
'''
inet6num: 1.2.3.0 - 1.2.3.255
netname: net-1

inet6num: 1.2.3.0/24
netname: net-1
'''
import logging; log = logging.getLogger(__name__)  # noqa E702
from IPy import IP
from ..errors import RPSLInetnumError, RPSLInvalidInetnumError

attribute = 'inet6num'


def parse(attr, value, strict=False, messages: list = None):
    assert attr == attribute, f'Unexpected {attr!r} in {attribute!r} parser'

    ok, message = True, ''
    if '-' in value:
        ip1, ip2 = map(str.strip, value.split('-', 1))
        try:
            ip1 = IP(ip1, ipversion=6)
        except ValueError as e:
            ok = False
            message = str(e)
        try:
            ip2 = IP(ip2, ipversion=6)
        except ValueError as e:
            ok = False
            message += (message and '; ') + str(e)
        if ok:
            value = f'{ip1} - {ip2}'
    else:
        try:
            value = IP(value, ipversion=6)
        except ValueError as e:
            ok = False
            message = str(e)
        if ok:
            value = f'{value[0]} - {value[-1]}'

    if message and messages:
        messages.append(message)
    if strict and not ok:
        raise RPSLInetnumError(None, None, message)
    return attr, value


def validate(obj):
    for i, entry in enumerate(obj.entries):
        attr, value = entry
        if i == 0:  # first line
            if attr != attribute:
                raise RPSLInvalidInetnumError(None, None,
                                            'Object is not a inet6num')
            obj.pk = value.strip().upper()
        else:
            if attr == 'netname':
                obj.pk += value.strip().upper()
                return  # found
    raise RPSLInvalidInetnumError(None, None, 'Inetnum object has no origin')

# vim:set ft=python ai et ts=4 sts=4 sw=4 cc=80:EOF #
