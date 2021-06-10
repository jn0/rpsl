#!python3
'''
'''
import logging; log = logging.getLogger(__name__)  # noqa E702
import os
import yaml

VERSION = 0
_config = {}
_loaded = set()


def load(filename):
    if filename in _loaded:
        log.warning('Config file %r is already loaded', filename)
        return {}
    _loaded.add(filename)
    with open(filename) as f:
        c = yaml.load(f, yaml.SafeLoader)
        assert c.get('version', -1) == VERSION, \
               f"config {filename!r}" \
               f" version {c.get('version')!r} != {VERSION!r}"
        if 'include' in c:
            dirname = os.path.dirname(filename)
            for name in c.pop('include', []):
                i = load(name if os.path.isabs(name)
                         else os.path.join(dirname, name))
                c.update(i)
        log.info('Config file %r has been loaded', filename)
        return c


def locate(name=None, suffix='.yaml'):
    filename = os.path.realpath(os.path.splitext(name or __file__)[0] + suffix)
    while True:
        if os.path.exists(filename):
            return filename
        d, n = os.path.split(filename)
        if d == '/' or not d:
            return None
        filename = os.path.join(os.path.dirname(d), n)


def config():
    if not _config:
        filename = locate()
        if not filename:
            log.fatal('No config.')
            return {}  # not the _config object!
        r = load(filename)
        _config.update(r)
    return _config


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    import sys, json  # noqa E401
    json.dump(config(), sys.stdout, indent=2, ensure_ascii=False)

# vim:set ft=python ai et ts=4 sts=4 sw=4 cc=80:EOF #
