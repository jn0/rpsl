#!python3
'''
route: 1.2.3.0/24
origin: as123
'''
import logging; log = logging.getLogger(__name__)  # noqa E702
from IPy import IP
from ..errors import RPSLRouteError, RPSLInvalidRouteError

attribute = 'route'


def parse(attr, value, strict=False, messages: list = None):
    assert attr == attribute, f'Unexpected {attr!r} in {attribute!r} parser'

    ok, message = True, ''
    if '/' not in value:
        message = f'Bad route value {value!r}'
        raise RPSLRouteError(None, None, message)

    try:
        value = IP(value, make_net=not strict)
    except ValueError as e:
        ok = False
        message = str(e)

    if message and messages:
        messages.append(message)
    if strict and not ok:
        raise RPSLRouteError(None, None, message)
    return attr, str(value)


def validate(obj):
    for i, entry in enumerate(obj.entries):
        attr, value = entry
        if i == 0:  # first line
            if attr != attribute:
                raise RPSLInvalidRouteError(None, None,
                                            'Object is not a route')
            obj.pk = value.strip().upper()
        else:
            if attr == 'origin':
                obj.pk += value.strip().upper()
                return  # found
    raise RPSLInvalidRouteError(None, None, 'Route object has no origin')

# vim:set ft=python ai et ts=4 sts=4 sw=4 cc=80:EOF #
