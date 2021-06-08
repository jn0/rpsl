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

_modules = {}
_parsers = {}
_validators = {}


def load_validators():
    if not _validators:
        _load()
    return _validators


def load_parsers():
    if not _parsers:
        _load()
    return _parsers


def _load():
    _modules.clear()
    _parsers.clear()
    _validators.clear()

    where = os.path.dirname(__file__)
    for f in os.listdir(where):
        name, ext = os.path.splitext(f)
        if ext not in ('.py',) or name.startswith('_'):
            continue

        module = __import__(__package__ + '.' + name, fromlist=(name,))
        if not hasattr(module, 'attribute'):
            log.warning('Ignored module %r -- no attribute name', module)
            continue
        if module.attribute in _modules:
            log.warning('Module for %r redefined', module.attribute)
        _modules[module.attribute] = module

        if not hasattr(module, 'parse'):
            log.warning('Ignored module %r -- no parser', module)
            continue
        log.info('module=%r attribute=%r', module, module.attribute)

        if module.attribute in _parsers:
            log.warning('Parser for %r redefined', module.attribute)
        _parsers[module.attribute] = module.parse

        if hasattr(module, 'validate'):
            if module.attribute in _validators:
                log.warning('Validator for %r redefined', module.attribute)
            _validators[module.attribute] = module.validate


# vim:set ft=python ai et ts=4 sts=4 sw=4 cc=80:EOF #
