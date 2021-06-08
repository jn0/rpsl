#!python3
'''
'''
import logging; log = logging.getLogger(__name__)  # noqa E702
from .object import RPSL
from .errors import RPSLSyntaxError


def parse(stream):
    '''
    `stream` must have `.readlines()` method

    returns a list of RPSL objects
    '''
    r = []
    o = []
    for ln, line in enumerate(stream.readlines()):
        line = line.rstrip()
        if not line:
            if o:
                r.append(RPSL(o))
                o.clear()
        else:
            if RPSL.is_continuation(line):
                if not o:
                    raise RPSLSyntaxError(ln, line, 'no line to continue')
            else:
                if not RPSL.is_valid_tagline(line):
                    raise RPSLSyntaxError(ln, line, 'bad tag line')
            o.append(line)
    if o:
        r.append(RPSL(o))
    return r


# vim:set ft=python ai et ts=4 sts=4 sw=4 cc=80:EOF #
