import datetime
from pydantic import BaseModel, validator

from fints.client import FinTS3PinTanClient, NeedTANResponse


class State(BaseModel):
    client: FinTS3PinTanClient = None
    dialog_data: bytes = None
    tan_data: NeedTANResponse = None
    tan_pending: bool = False

    class Config:
        arbitrary_types_allowed = True


class Account(BaseModel):
    name: str = None
    iban: str = None
    accountnumber: str = None
    bic: str = None
    code: str = None
    bank_name: str = None

    @validator("accountnumber")
    def check_iban_or_accoutnnumber(cls, accountnumber, values):
        if "iban" not in values and not accountnumber:
            raise ValueError("either iban or accountnumber is required")
        return accountnumber

    # TODO: for SEPAAccount we need at least the country code in the bic!
    # How do we deal with that???
    @validator("code")
    def check_bic_or_code(cls, code, values):
        if "bic" not in values and not code:
            raise ValueError("either bic or code is required")
        return code


# Connection holds connect data
# each endpoints (including connect) gets own model
# with TANin as base
class Connection(BaseModel):
    user_id: str
    pin: str
    server: str
    bank_identifier: str
    tan_mechanism: str


class GenericIn(BaseModel):
    connection: Connection = None
    account: Account = None
    tan: str = None


class ConnectInfo(GenericIn):
    pass


class BalanceIn(GenericIn):
    pass


class BalanceOut(BaseModel):
    amount: float
    currency: str
    status: str
    date: datetime.date


class AccountsIn(GenericIn):
    pass


class TransactionsIn(GenericIn):
    fromDate: datetime.date = None
    toDate: datetime.date = None


class TransactionOut(BaseModel):
    src: Account
    dst: Account = None
    amount: float
    currency: str
    date: datetime.date
    posting_text: str = None
    purpose: str = None
    transaction_code: int = None


# TODO: Maybe add TransactionsOut with opening and closing balance


class HoldingsIn(GenericIn):
    pass


class HoldingOut(BaseModel):
    isin: str
    name: str
    market_value: float
    value_symbol: str
    valuation_date: datetime.date
    pieces: float
    total_value: float
    acquisition_price: float
