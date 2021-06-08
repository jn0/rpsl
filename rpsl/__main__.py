#!python3
'''
'''
import logging; log = logging.getLogger(__name__)  # noqa E702
import sys
import os
from .parser import parse

logging.basicConfig(level=logging.INFO)

for arg in sys.argv[1:]:
    if os.path.exists(arg):
        with open(arg) as f:
            for o in parse(f):
                print(o, end='\n' + '~' * 80 + '\n')
    else:
        log.warning('No file %r', arg)
# vim:set ft=python ai et ts=4 sts=4 sw=4 cc=80:EOF #
