#!python3
'''
Every module in this directory MUST have
- name not starting with underscore
- string attribute `attribute` that holds the actual unmangled name of the RPSL
  attribute whose value is to be parsed
- callable method `parse` that match this signature:
    `parse(attr, value, strict=False, messages: list = None)`

'''
import logging; log = logging.getLogger(__name__)  # noqa E702
import os


def load_parsers():
    r = {}
    where = os.path.dirname(__file__)
    for f in os.listdir(where):
        name, ext = os.path.splitext(f)
        if ext not in ('.py',) or name.startswith('_'):
            continue
        module = __import__(__package__ + '.' + name, fromlist=(name,))
        if not hasattr(module, 'attribute'):
            log.warning('Ignored module %r -- no attribute name', module)
            continue
        if not hasattr(module, 'parse'):
            log.warning('Ignored module %r -- no parser', module)
            continue
        log.info('module=%r attribute=%r parser=%r',
                 module, module.attribute, module.parse)
        if module.attribute in r:
            log.warning('Parser for %r redefined', module.attribute)
        r[module.attribute] = module.parse
    return r


# vim:set ft=python ai et ts=4 sts=4 sw=4 cc=80:EOF #
