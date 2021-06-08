#!python3
'''
'''
import logging; log = logging.getLogger(__name__)  # noqa E702
from .errors import RPSLAttributeError
from .attribute import load_parsers, load_validators


class RPSL:
    ATTRIBUTE_SIZE = 16
    _PARSERS = {}
    _VALIDATORS = {}

    @classmethod
    def initialize(klass):
        if not klass._PARSERS:
            klass._PARSERS.update(load_parsers())
        if not klass._VALIDATORS:
            klass._VALIDATORS.update(load_validators())

    @staticmethod
    def format_attribute(attr, attribute_size=ATTRIBUTE_SIZE):
        return (attr + ':').ljust(attribute_size)

    @staticmethod
    def is_continuation(line):
        return line and line.startswith((' ', '\t', '+'))

    @staticmethod
    def is_valid_line(line):
        return ':' in line and \
               not any(c.isspace() for c in line.split(':', 1)[0])

    @staticmethod
    def format_line(line):
        if RPSL.is_valid_line(line):
            attribute, value = line.split(':', 1)
            return RPSL.format_attribute(attribute) + value.lstrip()
        return line

    def __init__(self, lines: list, strict=False):
        self.strict = strict                    # flag
        self.lines = [line for line in lines]   # sorta copy
        self.entries = []                       # parsed entries
        self.object_class = None                # object class
        self.pk = None                          # primary lookup key

        self.parse_object()

        validator = RPSL._VALIDATORS.get(self.object_class)
        if validator:
            assert callable(validator), validator
            validator(self)  # may update self.pk

    @classmethod
    def _null_parser(cls, attribute, value, strict=None, messages=None):
        '''the very basic parser'''
        return attribute, value

    def get_parser(self, attribute):
        '''to be implemented yet'''
        if self.strict and attribute not in RPSL._PARSERS:
            raise RPSLAttributeError(self._ln, self._line,
                                     f'Unknown attribute {attribute!r}')
        return RPSL._PARSERS.get(attribute, self._null_parser)

    def parse_object(self):
        entry = self._ln = self._line = None
        for self._ln, self._line in enumerate(self.lines):
            if self._ln == 0:
                self.object_class, self.pk = self._line.split(':', 1)
            if self.is_continuation(self._line):
                entry += self._line[1:]
            else:
                if entry:
                    self.entries.append(self.parse_entry(entry))
                entry = self._line
        else:
            if entry:
                self.entries.append(self.parse_entry(entry))
        self._ln = self._line = None

    def parse_entry(self, line):
        attribute, value = line.split(':', 1)  # must work
        messages = []
        parser = self.get_parser(attribute)
        rc = parser(attribute, value.lstrip(),
                    strict=self.strict, messages=messages)
        if messages:
            log.error('line #%d has errors:\n%s',
                      self._ln, '\n'.join(messages))
        return rc

    def __str__(self):
        return '\n'.join(map(self.format_line, self.lines))


# vim:set ft=python ai et ts=4 sts=4 sw=4 cc=80:EOF #
