#!python3
'''
'''
import logging; log = logging.getLogger(__package__)  # noqa E702
import logging.config
import sys
import os
from .parser import parse
from .config import config

logging.basicConfig(level=logging.INFO)
cf = config()
if 'logging' in cf:
    lcf = cf.pop('logging')
    if lcf:
        logging.config.dictConfig(lcf)

log.info('begin')
try:
    for arg in sys.argv[1:]:
        if os.path.exists(arg):
            with open(arg) as f:
                for o in parse(f, exceptions=False):
                    print(o, end='\n' + '~' * 80 + '\n')
        else:
            log.warning('No file %r', arg)
finally:
    log.info('end')
# vim:set ft=python ai et ts=4 sts=4 sw=4 cc=80:EOF #
