from schwifty import IBAN, BIC
from fints.models import SEPAAccount

from models import Account


def get_iban_bic(iban_str, bic_str, country_code):
    iban = None
    number = None
    bic = None
    code = None

    if not iban_str:
        iban_str = ""
    if not bic_str:
        bic_str = ""

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

    if iban:
        return iban.compact, iban.account_code, iban.bic.compact, iban.bank_code
    else:
        return None, number, None, code


def make_SEPAAccount(account: Account):
    return SEPAAccount(
        iban=account.iban,
        bic=account.bic,
        accountnumber=account.accountnumber,
        subaccount=None,
        blz=account.code,
    )
