#!python3
'''
'''
import logging; log = logging.getLogger(__name__)  # noqa E702
from .errors import RPSLAttributeError


class RPSL:
    ATTRIBUTE_SIZE = 16
    _PARSERS = {}

    @staticmethod
    def format_attribute(attr, attribute_size=ATTRIBUTE_SIZE):
        return (attr + ':').ljust(attribute_size)

    @staticmethod
    def is_continuation(line):
        return line and line.startswith((' ', '\t', '+'))

    @staticmethod
    def is_valid_tagline(line):
        return ':' in line and \
               not any(c.isspace() for c in line.split(':', 1)[0])

    @staticmethod
    def format_line(line):
        if RPSL.is_valid_tagline(line):
            attribute, value = line.split(':', 1)
            return RPSL.format_attribute(attribute) + value.lstrip()
        return line

    def __init__(self, lines: list, strict=False):
        self.strict = strict
        self.lines = [line for line in lines]  # sorta copy...
        self.entries = []
        entry = None
        self._ln = self._line = None
        for self._ln, self._line in enumerate(self.lines):
            if self.is_continuation(self._line):
                entry += self._line[1:]
            else:
                if entry:
                    self.entries.append(self.parse(entry))
                entry = self._line

    @classmethod
    def _null_parser(cls, attribute, value):
        '''the very basic parser'''
        return attribute, value

    def get_parser(self, attribute):
        '''to be implemented yet'''
        if self.strict and attribute not in RPSL._PARSERS:
            raise RPSLAttributeError(self._ln, self._line,
                                     f'Unknown attribute {attribute!r}')
        return RPSL._PARSERS.get(attribute, self._null_parser)

    def parse(self, line):
        attribute, value = line.split(':', 1)  # must work
        return self.get_parser(attribute)(attribute, value.lstrip())

    def __str__(self):
        return '\n'.join(map(self.format_line, self.lines))


# vim:set ft=python ai et ts=4 sts=4 sw=4 cc=80:EOF #
