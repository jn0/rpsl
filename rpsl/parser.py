#!python3
'''
'''
import logging; log = logging.getLogger(__name__)  # noqa E702
from .object import RPSL
from .errors import Error, RPSLSyntaxError


def parse(stream, exceptions=True):
    '''
    `stream` must have `.readlines()` method

    returns a list of RPSL objects
    '''
    r = []
    o = []
    RPSL.initialize()
    for ln, line in enumerate(stream.readlines()):
        line = line.rstrip()
        log.info('%3d: %r', ln + 1, line)
        if not line:
            if o:
                try:
                    t = RPSL(o)
                except Error as e:
                    t = None
                    log.error('%d: %s', ln + 1, e)
                    if exceptions:
                        raise
                r.append(t)
                o.clear()
        else:
            if RPSL.is_continuation(line):
                if not o:
                    raise RPSLSyntaxError(ln, line, 'no line to continue')
            else:
                if not RPSL.is_valid_line(line):
                    raise RPSLSyntaxError(ln, line, 'bad line format')
            o.append(line)
    if o:
        try:
            t = RPSL(o)
        except Error as e:
            t = None
            log.error('%d: %s', ln + 1, e)
            if exceptions:
                raise
        r.append(t)
    return r


# vim:set ft=python ai et ts=4 sts=4 sw=4 cc=80:EOF #
