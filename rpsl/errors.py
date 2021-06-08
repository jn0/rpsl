#!python3
'''
'''
import logging; log = logging.getLogger(__name__)  # noqa E702


class Error(Exception):

    def __init__(self, *av, **kw):
        super().__init__(*av, **kw)
        log.error('%s: %r %r', self.__class__.__name__, av, kw)


class RPSLSyntaxError(Error): pass  # noqa E702
class RPSLValidationError(Error): pass  # noqa E702

class RPSLAttributeError(RPSLSyntaxError): pass  # noqa E702

class RPSLOriginError(RPSLAttributeError): pass  # noqa E702
class RPSLRouteError(RPSLAttributeError): pass  # noqa E702
class RPSLInetnumError(RPSLAttributeError): pass  # noqa E702

class RPSLInvalidRouteError(RPSLValidationError): pass  # noqa E702
class RPSLInvalidInetnumError(RPSLValidationError): pass  # noqa E702

# vim:set ft=python ai et ts=4 sts=4 sw=4 cc=80:EOF #
