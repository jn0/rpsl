#!python3
'''
'''
import logging; log = logging.getLogger(__name__)  # noqa E702
import os
import yaml

_config = {}


def config():
    if not _config:
        filename = os.path.splitext(__file__)[0] + '.yaml'
        with open(filename) as f:
            c = yaml.load(f, yaml.SafeLoader)
        _config.update(c)
    return _config


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    import sys, json  # noqa E401
    json.dump(config(), sys.stdout, indent=2, ensure_ascii=False)

# vim:set ft=python ai et ts=4 sts=4 sw=4 cc=80:EOF #
