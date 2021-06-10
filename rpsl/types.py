#!python3
'''
'''
import logging; log = logging.getLogger(__name__)  # noqa E702
from string import ascii_letters, digits

ascii_letters_or_digits = ascii_letters + digits
id_symbols = ascii_letters_or_digits + '-_'


class TYPES:

    @staticmethod
    def object_name(x):           # [a-z]([a-z0-9_-]*[a-z0-9])?
        return len(x) >= 1 and \
               x[0] in ascii_letters and \
               all(c in id_symbols for c in x) and \
               x[-1] in ascii_letters_or_digits

    @staticmethod
    def as_number(x):             # 'AS' number
        return len(x) > 2 and x.upper().startswith('AS') and x[2:].isnumeric()

    @staticmethod
    def ipv4_address(x):          # dotted-quad
        if 7 <= len(x) <= 15 and x.count('.') == 3:
            try:
                o = [int(q, 10) for q in x.split('.')]
            except ValueError:
                return False
            return len(o) == 4 and all(0 <= q <= 255 for q in o)
        return False

    @staticmethod
    def address_prefix(x):        # <ipv4-address> '/' number
        if '/' in x:
            a, b = x.split('/', 1)
            if TYPES.ipv4_address(a):
                try:
                    b = int(b, 10)
                except ValueError:
                    return False
                return 0 < b <= 32
        return False

    @staticmethod
    def range_op(x):
        if x in ('+', '-'):
            return True
        if '-' in x:
            try:
                x = [int(i, 10) for i in x.split('-', 1)]
            except ValueError:
                return False
            return len(x) == 2 and all(0 < i <= 32 for i in x) and x[0] <= x[1]
        try:
            x = int(x, 10)
        except ValueError:
            return False
        return 0 < x <= 32

    @staticmethod
    def address_prefix_range(x):
        # (address-prefix|address-prefix-set) '^' range-op
        if '^' not in x:
            return False
        if x.startswith('{'):
            p, r = x.rsplit('^', 1)
            return TYPES.address_prefix_set(p) and TYPES.range_op(r)
        else:
            p, r = x.split('^', 1)
            return TYPES.address_prefix(p) and TYPES.range_op(r)

    @staticmethod
    def address_prefix_set(x):    # '{' <address-prefix-range> '}'
        if x.startswith('{') and x.endswith('}'):
            return TYPES.address_prefix_range(x[1:-1].strip())
        return False

    @staticmethod
    def date(x):                  # YYYYMMDD
        if len(x) == 8 and x.isnumeric():
            try:
                y, m, d = int(x[0:4], 10), int(x[4:6], 10), int(x[6:8], 10)
            except ValueError:
                return False
            return (1970 <= y <= 3000) and (1 <= m <= 12) and (1 <= d <= 31)
        return False

    @staticmethod
    def email_address(x):         # RFC822
        return '@' in x and '.' in x.split('@', 1)[-1]

    @staticmethod
    def dns_name(x):              # RFC1034
        return len(x) > 2 and '.' in x

    @staticmethod
    def nic_handle(x):            # <object-name>
        return TYPES.object_name(x)

    @staticmethod
    def free_form(x):
        return True

    @staticmethod
    def registry_name(x):         # RFC2622.A
        return TYPES.object_name(x)

    @staticmethod
    def list(x):                  # comma-delimited list of <types>
        return False

    @staticmethod
    def scheme_id(x):             # NONE, MAIL-FROM, PGP-KEY and CRYPT-PW
        return x.lower() in ('none', 'mail-from', 'pgp-key', 'crypt-pw')

    @staticmethod
    def auth_info(x):             # junk
        return True

    @staticmethod
    def auth(x):                  # <scheme-id> ' ' <auth-info>
        s, a = x.split(maxsplit=1)
        return TYPES.scheme_id(s) and TYPES.auth_info(a)

    @staticmethod
    def changed(x):               # <email-address> ' ' <date>
        m, d = x.split(maxsplit=1)
        return TYPES.email_address(m) and TYPES.date(d)

    @staticmethod
    def phone(x):  # +<country-code> <city> <subscriber> [ext. <extension>]
        x = x.split()
        if len(x) >= 3 and x[0].startswith('+'):
            try:
                cc, df, uu = [int(i, 10) for i in x[:3]]
            except ValueError:
                return False
            if len(x) > 3 and len(x) == 5 and x[3].lower() == 'ext.':
                try:
                    int(x[4], 10)
                except ValueError:
                    return False
                return True
        return False

    @staticmethod
    def date_time(x):             # 2020-12-25T16:16:09Z
        if len(x) == 20 and 'T' in x.upper() and x.upper().endswith('Z'):
            try:
                y, m, d, H, M, S = (int(x[:4], 10), int(x[5:7], 10),
                                    int(x[8:10], 10), int(x[11:13], 10),
                                    int(x[14:16], 10), int(x[17:19]))
            except ValueError:
                return False
            return (1970 <= y <= 3000) and (1 <= m <= 12) and (1 <= d <= 31) \
                and (0 <= H <= 23) and (0 <= M <= 59) and (0 <= S <= 59)

        return False


def match_type(config, value, typespec):
    result = True
    # types = config.get('rpsl', {}).get('types')

    if hasattr(TYPES, typespec.replace('-', '_')):
        chk = getattr(TYPES, typespec.replace('-', '_'))
        result = chk(value)
    log.debug('match_type(value=%r type=%r): %r', value, typespec, result)
    return result


# vim:set ft=python ai et ts=4 sts=4 sw=4 cc=80:EOF #
