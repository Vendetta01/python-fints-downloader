from schwifty import IBAN, BIC
from urllib.parse import urljoin
import json
from datetime import datetime, date


def get_iban_bic(iban_str, bic_str, country_code):
    iban = None
    number = None
    bic = None
    code = None

    if not iban_str:
        iban_str = ''
    if not bic_str:
        bic_str = ''

    try:
        iban = IBAN(iban_str)
        number = iban.account_code
    except ValueError:
        if iban_str.isnumeric():
            number = iban_str
    else:
        bic = iban.bic

    if not bic:
        try:
            bic = BIC(bic_str)
            code = bic.country_bank_code
        except ValueError:
            try:
                bic = BIC.from_bank_code(country_code, bic_str)
                code = bic.country_bank_code
            except ValueError:
                if bic_str.isnumeric():
                    code = bic_str

    if bic and number and not iban:
        try:
            iban = IBAN.generate(country_code, bic.country_bank_code, number)
        except ValueError:
            pass

    return iban, number, bic, code


def get_value(dictionary, *args, dst_type=None):
    val = dictionary
    for arg in args:
        val = val.get(arg)
        if val is None:
            return None

    if dst_type and val:
        return dst_type(val)
    return val


def format_backend_url(ftsdb, endpoint):
    return urljoin(urljoin(
        f"{ftsdb.server}:{ftsdb.port}",
        ftsdb.base_url),
        endpoint)


class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime) or isinstance(o, date):
            return o.isoformat()
        return json.JSONEncoder.default(self, o)
