#!python3
'''
'''
import logging; log = logging.getLogger(__name__)  # noqa E702
from time import perf_counter
from .object import RPSL
from .errors import Error, RPSLSyntaxError


def parse(stream, exceptions=True):
    '''
    `stream` must have `.readlines()` method

    returns a list of RPSL objects
    '''
    t1 = perf_counter()
    try:
        r = []
        o = []
        RPSL.initialize()
        for ln, line in enumerate(stream.readlines()):
            if '#' in line:
                line = line.split('#', 1)[0]
            line = line.rstrip()
            log.debug('%3d: %r', ln + 1, line)
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
        else:
            lines = ln + 1
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
    finally:
        t2 = perf_counter()
        log.info('Parsed %d for %.3f seconds, %.0f LPS',
                 lines, t2 - t1, float(lines) / (t2 - t1))


# vim:set ft=python ai et ts=4 sts=4 sw=4 cc=80:EOF #
