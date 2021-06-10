#!python3
'''
'''
import logging; log = logging.getLogger(__name__)  # noqa E702
from .errors import RPSLAttributeError
from .attribute import load_parsers, load_validators
from .config import config
from .types import match_type


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
        if RPSL.is_continuation(line):
            if line.startswith('+'):
                return line.rstrip()  # as is
            return ' '.ljust(RPSL.ATTRIBUTE_SIZE) + line.strip()
        return '?' + line

    def __init__(self, lines: list, strict=False):
        self.strict = strict                    # flag
        self.lines = [line for line in lines]   # sorta copy
        self.entries = []                       # parsed entries
        self.object_class = None                # object class
        self.pk = None                          # primary lookup key

        self.cf = config()  # ref to global config

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
        seen = {}
        spec = None
        types = {}
        tags = set()

        entry = self._ln = self._line = None
        for self._ln, self._line in enumerate(self.lines):
            if self._ln == 0:
                self.object_class, self.pk = \
                    list(map(str.strip, self._line.split(':', 1)))
                spec = self.cf.get('rpsl', {}) \
                              .get('class', {}) \
                              .get(self.object_class)
                types = {entry['name']: entry['type'] for entry in spec} \
                    if spec else {}
                tags = {entry['name'] for entry in spec} if spec else set()
            if self.is_continuation(self._line):
                entry += self._line[1:]
            else:
                if entry:
                    self.entries.append(self.parse_entry(entry, types))
                    tag = self.entries[-1][0]
                    seen[tag] = seen.get(tag, 0) + 1
                entry = self._line
        else:
            if entry:
                self.entries.append(self.parse_entry(entry, types))
                tag = self.entries[-1][0]
                seen[tag] = seen.get(tag, 0) + 1
        self._ln = self._line = None

        if not spec:
            log.warning('No spec for %r', self.object_class)
            return

        if not self.object_class:
            self.object_class = 'UnKnOwN'

        mandatory = {entry['name']
                     for entry in spec
                     if not entry['optional']}
        lost = [tag for tag in mandatory if tag not in seen]
        if lost:
            raise RPSLAttributeError(None, None,
                                     f'{self.object_class}'
                                     f' lost {", ".join(lost)}')
        log.debug('Mandatory fields ok for %r %r', self.object_class, self.pk)

        extras = {e[0] for e in self.entries if e[0] not in tags}
        if extras:
            raise RPSLAttributeError(None, None,
                                     f'{self.object_class}'
                                     f' extra {", ".join(extras)}')

        multiple = {entry['name'] for entry in spec if entry['multiple']}
        repeated = [tag for tag in tags
                    if tag not in multiple and seen.get(tag, 0) > 1]
        if repeated:
            raise RPSLAttributeError(None, None,
                                     f'{self.object_class} repeated single'
                                     f' fileds {", ".join(repeated)}')

    def parse_entry(self, line, types):
        attribute, value = line.split(':', 1)  # must work
        value = value.lstrip()
        messages = []
        if attribute in types and types[attribute]:
            spec = types[attribute]
            is_list = spec.startswith('list:')
            if is_list:
                spec = spec.split(':', 1)[-1]
            spec = spec.split('|')
            for val in map(str.strip, value.split(',')):
                if not any(match_type(self.cf, val, t) for t in spec):
                    messages.append(f'{val!r} does not match {spec!r}')
            pass  # TODO use types[attribute] to validate too
        parser = self.get_parser(attribute)
        rc = parser(attribute, value, strict=self.strict, messages=messages)
        if messages:
            log.error('line #%d has errors:\n%s',
                      self._ln, '\n'.join(messages))
        return rc

    def __str__(self):
        return '\n'.join(map(self.format_line, self.lines))


# vim:set ft=python ai et ts=4 sts=4 sw=4 cc=80:EOF #
