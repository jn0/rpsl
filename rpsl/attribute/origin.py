#!python3
'''
'''
import logging; log = logging.getLogger(__name__)  # noqa E702
from ..errors import RPSLOriginError

attribute = 'origin'


def parse(attr, value, strict=False, messages: list = None):
    assert attr == attribute, f'Unexpected {attr!r} in {attribute!r} parser'
    ok = value.upper().startswith('AS') and value[2:].isnumeric()
    message = f'Bad origin value {value!r}'
    if messages and not ok:
        messages.append(message)
    if strict and not ok:
        raise RPSLOriginError(None, None, message)

# vim:set ft=python ai et ts=4 sts=4 sw=4 cc=80:EOF #
