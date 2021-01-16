import logging
from fastapi import FastAPI, HTTPException
from typing import List
import sys
sys.path.append("..")
from fints.client import FinTS3PinTanClient, NeedTANResponse  # noqa: E402
from fints.exceptions import FinTSClientPINError,\
    FinTSDialogInitError  # noqa: E402

from models import State, GenericIn, AccountsIn, Account,\
    BalanceIn, BalanceOut, TransactionsIn, TransactionOut,\
    HoldingsIn, HoldingOut  # noqa: E402
from utils import get_iban_bic, make_SEPAAccount  # noqa: E402


# TODO: Make multi user possible (an account can login only one
#       at a time but multiple different accounts can perform actions
#       simultaneously)
# TODO: authentication???

def try_request(func_name, tan, *args, **kwargs):
    global state

    if not connected():
        raise HTTPException(status_code=405, detail="Not connected")

    fints_func = getattr(state.client, func_name)

    if tan and state.tan_pending:
        # TODO: maybe resume_dialog()?
        response = state.client.send_tan(state.tan_data, tan)
        state.tan_data = None
        state.tan_pending = False
        if not response:
            raise HTTPException(
                status_code=403,
                detail="Invalid TAN")
    else:
        response = fints_func(*args, **kwargs)
        if isinstance(response, NeedTANResponse):
            # TAN requried
            state.tan_data = response
            state.tan_pending = True
            raise HTTPException(
                status_code=401,
                detail=f"TAN required: {state.tan_data.challenge_html}")

    return response


logging.basicConfig(level=logging.INFO)

state = State()

app = FastAPI()


@app.get("/connect")
def connected():
    global state
    if not state.client:
        return False
    return True


@app.post("/connect")
def connect(conInfo: GenericIn):
    global state

    if state.client:
        # Already connected
        raise HTTPException(status_code=400, detail="Already connected")
    if state.tan_pending:
        # tan required
        raise HTTPException(status_code=401, detail="TAN required")

    state.client = FinTS3PinTanClient(
        bank_identifier=conInfo.connection.bank_identifier,
        user_id=conInfo.connection.user_id,
        pin=conInfo.connection.pin,
        server=conInfo.connection.server)

    # Fetch TAN mechanism and catch if something is going wrong
    try:
        state.client.fetch_tan_mechanisms()
    except FinTSDialogInitError:
        state.client = None
        raise HTTPException(
            status_code=400,
            detail=("Error during dialog initialisation: server "
                "unavailable or authentication wrong?"))
    except FinTSClientPINError:
        state.client = None
        raise HTTPException(
            status_code=401,
            detail="Error during dialog initialisation: PIN wrong?")

    # set TAN mechanism
    if conInfo.connection.tan_mechanism in state.client.get_tan_mechanisms():
        state.client.set_tan_mechanism(conInfo.connection.tan_mechanism)
    else:
        state.client = None
        raise HTTPException(
            status_code=400,
            detail=(f"TAN mechanism '{conInfo.connection.tan_mechanism}'"
                "not supported by account"))


@app.post("/disconnect")
def disconnect():
    global state

    # close pending dialog
    if state.dialog_data:
        with state.client.resume_dialog(state.dialog_data):
            state.dialog_data = None

    state.tan_pending = False
    state.client = None


# TODO: Refactor
@app.post("/accounts", response_model=List[Account])
def get_accounts(accountsIn: AccountsIn = None):
    if not connected():
        connect(accountsIn)

    sepa_accounts = try_request('get_sepa_accounts', accountsIn.tan)

    info = try_request('get_information', accountsIn.tan)

    disconnect()

    # Merge account sources
    account_list = []
    for sepa_account in sepa_accounts:
        account_list.append(Account(
            name=None,
            iban=sepa_account.iban,
            accountnumber=sepa_account.accountnumber,
            bic=sepa_account.bic,
            code=sepa_account.blz,
        ))

    # Add accounts from get_information
    for info_account in info['accounts']:
        iban = info_account['iban']
        acc_num = info_account['account_number']
        acc_type = info_account['type']
        acc_product_name = info_account['product_name']
        if (iban and any(acc.iban == iban for acc in account_list)) or \
                (acc_num and any(acc.accountnumber == acc_num
                for acc in account_list)):
            account_list.append(Account(
                name=f"{acc_type} {acc_product_name}",
                iban=iban,
                accountnumber=acc_num,
                bic=None,
                code=info_account['bank_identifier'].bank_code
            ))

    return account_list


@app.post("/balance")
def get_balance(balanceIn: BalanceIn):
    if not connected():
        connect(balanceIn)

    balance = try_request(
        'get_balance',
        balanceIn.tan,
        make_SEPAAccount(balanceIn.account))

    disconnect()

    return BalanceOut(
        amount=balance.amount.amount,
        currency=balance.amount.currency,
        status=balance.status,
        date=balance.date)


@app.post("/transactions", response_model=List[TransactionOut])
def get_transactions(transactionsIn: TransactionsIn):
    if not connected():
        connect(transactionsIn)

    transactions = try_request(
        'get_transactions',
        transactionsIn.tan,
        make_SEPAAccount(transactionsIn.account),
        transactionsIn.fromDate,
        transactionsIn.toDate)

    disconnect()

    # TODO: Maybe include opening and closing balance in result

    transaction_list = []
    src = transactionsIn.account
    for transaction in transactions:
        iban, number, bic, code = get_iban_bic(
            transaction.data.get('applicant_iban'),
            transaction.data.get('applicant_bin'),
            'DE')

        dst = None
        if (iban or number) and (bic or code):
            dst = Account(
                iban=iban,
                accountnumber=number,
                bic=bic,
                code=code,
                name=transaction.data.get('applicant_name')
            )
        transaction_list.append(TransactionOut(
            src=src,
            dst=dst,
            amount=transaction.data.get('amount').amount,
            currency=transaction.data.get('amount').currency,
            date=transaction.data.get('date'),
            posting_text=transaction.data.get('posting_text'),
            purpose=transaction.data.get('purpose'),
            transaction_code=transaction.data.get('transaction_code')
        ))

    return transaction_list


@app.post("/holdings", response_model=List[HoldingOut])
def get_holdings(holdingsIn: HoldingsIn):
    if not connected():
        connect(holdingsIn)

    holdings = try_request(
        'get_holdings',
        holdingsIn.tan,
        make_SEPAAccount(holdingsIn.account))

    disconnect()

    holding_list = []
    for holding in holdings:
        holding_list.append(HoldingOut(
            isin=holding.ISIN,
            name=holding.name,
            market_value=holding.market_value,
            value_symbol=holding.value_symbol,
            valuation_date=holding.valuation_date,
            pieces=holding.pieces,
            total_value=holding.total_value,
            acquisition_price=holding.acquisitionprice
        ))

    return holding_list
