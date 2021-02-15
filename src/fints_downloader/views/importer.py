import logging
from decimal import Decimal
import dateparser
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views.generic.edit import FormView
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin
import requests
import json

from fints_downloader.forms import (
    ImportAccountsForm,
    ImportTransactionsForm,
    ImportHoldingsForm,
    TANForm,
)
from fints_downloader.models.account import Account
from fints_downloader.models.banklogin import BankLogin
from fints_downloader.models.holding import Holding
from fints_downloader.models.fintsdownloaderbackend import FinTSDownloaderBackend
from fints_downloader.models.transaction import Transaction
from fints_downloader.models.types import AccountTypes
from backend.models import (
    GenericIn,
    Connection,
    Account as BackendAccount,
    TransactionsIn,
)
from fints_downloader.utils import get_value, format_backend_url, DateTimeEncoder

logger = logging.getLogger(__name__)


class ImportFinTSGenericView(FormView):
    template_name = "importer.html"
    form_class = ImportAccountsForm
    fd_backend_endpoint = "accounts"
    redirect_dst = "/fints_downloader/"

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        context = {"form": form, "error_message": None}
        connection_error = False
        fd_backend_base_url = FinTSDownloaderBackend.objects.first()
        if not fd_backend_base_url:
            connection_error = True
            context["error_message"] = "No backend server available!"
            return render(request, self.template_name, context)
        fd_backend_url_connect = format_backend_url(fd_backend_base_url, "connect")
        fd_backend_url_disconnect = format_backend_url(
            fd_backend_base_url, "disconnect"
        )

        # Reset session
        # TODO: use https
        try:
            r = requests.get(fd_backend_url_connect)
        except requests.exceptions.RequestException as e:
            connection_error = True
            context["error_message"] = e

        if not connection_error:
            if r.json():
                requests.post(fd_backend_url_disconnect)
            for key in (
                "fd_backend_url",
                "fd_backend_payload",
                "bank_login_id",
                "tan_challenge",
                "import_data_callback",
                "account_id",
            ):
                if key in request.session:
                    del request.session[key]

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        redirect_dst = self.redirect_dst
        fd_backend_url = format_backend_url(
            FinTSDownloaderBackend.objects.first(), self.fd_backend_endpoint
        )
        bank_login_id = None
        bank_login = None
        account_id = None
        account = None

        if form.is_valid():
            bank_login_id = request.POST.get("bank_login")
            bank_login = BankLogin.objects.filter(pk=bank_login_id).first()

            if not bank_login:
                account_id = request.POST.get("account")
                account = Account.objects.filter(pk=account_id).first()
                bank_login = account.bank_login
                bank_login_id = bank_login.id

            backend_connection = Connection(
                user_id=bank_login.user_id,
                pin=bank_login.password,
                server=bank_login.server,
                bank_identifier=bank_login.code,
                tan_mechanism=bank_login.tan_mechanism,
            )
            backend_account = None
            if account:
                backend_account = BackendAccount(
                    name=account.name,
                    iban=account.iban,
                    accountnumber=account.number,
                    bic=account.bic,
                )
            fd_backend_payload = json.dumps(
                self.payload_from_post(
                    backend_connection, backend_account, request.POST
                ),
                cls=DateTimeEncoder,
            )

            request.session["import_data_callback"] = type(self).__name__
            request.session["fd_backend_payload"] = fd_backend_payload
            request.session["fd_backend_url"] = fd_backend_url
            request.session["account_id"] = account_id
            request.session["bank_login_id"] = bank_login_id

            r = requests.post(fd_backend_url, data=fd_backend_payload)

            if r.status_code == 401:
                # TAN required
                request.session["tan_challenge"] = r.json()
                redirect_dst = "/fints_downloader/import/tan/"
            elif r.status_code != 200:
                return HttpResponse(
                    content=r.content,
                    status=r.status_code,
                    content_type=r.headers["Content-Type"],
                )
            else:
                self.import_data(bank_login, account, r.json())

            return HttpResponseRedirect(redirect_dst)

        context = request.context
        context["form"] = form
        return render(request, self.template_name, context)

    def import_data(self, bank_login, account, response):
        raise Exception("Not implemented yet")

    def payload_from_post(
        self, backend_connection, backend_account, post_data
    ):  # noqa: E501
        return GenericIn(connection=backend_connection, account=backend_account).dict()


class ImportAccountsView(LoginRequiredMixin, ImportFinTSGenericView):
    template_name = "importer.html"
    form_class = ImportAccountsForm
    fd_backend_endpoint = "accounts"

    def import_data(self, bank_login, account, response):
        for response_account in response:
            # TODO: determine account type
            account_type = AccountTypes.CHECKING
            # TODO: check if bic/blz matches bank_login.bank
            # TODO: automatically converts foreign accounts to owned accounts
            account = Account(
                bank_login=bank_login,
                iban=response_account.get("iban"),
                number=Decimal(response_account.get("accountnumber")),
                bic=response_account.get("bic"),
                type=account_type,
                name=response_account.get("name"),
            )
            logger.info("Importing account: %s", account)
            account.save()


# FIXME: change bank etc.
class ImportTransactionsView(LoginRequiredMixin, ImportFinTSGenericView):
    template_name = "importer.html"
    form_class = ImportTransactionsForm
    fd_backend_endpoint = "transactions"

    def import_data(self, bank_login, account, response):
        # Source Account is per definition the queried account
        # src_account = Account.objects.filter(Q(iban=))
        src_account = account

        for trans in response:
            dst_account = None
            dst = trans.get("dst")

            if dst:
                dst_account = Account.objects.filter(
                    (Q(iban=dst.get("iban")) | Q(number=trans.get("accountnumber")))
                    & Q(bic=dst.get("bic"))
                ).first()
                if not dst_account:
                    dst_account = Account(
                        bank_login=None,
                        iban=dst.get("iban"),
                        number=get_value(
                            trans, "dst", "accountnumber", dst_type=Decimal
                        ),
                        bic=dst.get("bic"),
                        type=AccountTypes.FOREIGN,
                        name=trans.get("name"),
                    )
                    logger.info("Saving new account instance: %s", dst_account)
                    dst_account.save()
                    dst_account.refresh_from_db()

            Transaction(
                amount=Decimal(trans.get("amount")).quantize(Decimal("0.01")),
                currency=trans.get("currency"),
                src=src_account,
                dst=dst_account,
                date=trans.get("date"),
                posting_text=trans.get("posting_text"),
                purpose=trans.get("purpose"),
                transaction_code=Decimal(trans.get("transaction_code")),
            ).save()

    def payload_from_post(
        self, backend_connection, backend_account, post_data
    ):  # noqa: E501
        return TransactionsIn(
            connection=backend_connection,
            account=backend_account,
            fromDate=dateparser.parse(
                post_data.get("fromDate"), settings={"DATE_ORDER": "DMY"}
            ),
            toDate=dateparser.parse(
                post_data.get("toDate"), settings={"DATE_ORDER": "DMY"}
            ),
        ).dict()


class ImportHoldingsView(LoginRequiredMixin, ImportFinTSGenericView):
    template_name = "importer.html"
    form_class = ImportHoldingsForm
    fd_backend_endpoint = "holdings"

    def import_data(self, bank_login, account, response):
        # TODO: Check existence???
        for backendHolding in response:
            Holding(
                account=account,
                isin=backendHolding.get("isin"),
                name=backendHolding.get("name"),
                market_value=backendHolding.get("market_value"),
                currency=backendHolding.get("value_symbol"),
                valuation_date=backendHolding.get("valuation_date"),
                pieces=backendHolding.get("pieces"),
                total_value=backendHolding.get("total_value"),
                acquisitionprice=backendHolding.get("acquisitionprice"),
            ).save()


class TANView(LoginRequiredMixin, FormView):
    template_name = "importer_tan.html"
    form_class = TANForm

    def get(self, request, *args, **kwargs):
        # fd_backend_payload = request.session.get('fd_backend_payload')
        fd_backend_url = request.session.get("fd_backend_url")
        tan_challenge = request.session.get("tan_challenge")

        # FIXME: convert string back to dict()/json()
        # account_iban = get_value(fd_backend_payload, 'account', 'iban')
        # account_number = get_value(
        #    fd_backend_payload, 'account', 'accountnumber')
        account_iban = None
        account_number = None

        form = self.form_class(initial={})

        context = {
            "form": form,
            "tan_challenge": tan_challenge,
            "account_iban": account_iban,
            "account_number": account_number,
            "endpoint_url": fd_backend_url,
        }

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            redirect_dst = "/fints_downloader/"

            fd_backend_payload = request.session.get("fd_backend_payload")
            fd_backend_url = request.session.get("fd_backend_url")
            import_data_callback = request.session.get("import_data_callback")
            callingForm = globals()[import_data_callback]()
            account_id = request.session.get("account_id")
            bank_login_id = request.session.get("bank_login_id")

            tan = request.POST.get("tan")
            fd_backend_payload = json.dumps(
                json.loads(fd_backend_payload).update({"tan": tan}), cls=DateTimeEncoder
            )

            account = None
            bank_login = None
            if account_id:
                account = Account.objects.filter(pk=account_id).first()
            if bank_login_id:
                bank_login = BankLogin.objects.filter(pk=bank_login_id).first()

            if (
                not tan
                or not fd_backend_payload
                or not fd_backend_url
                or not form
                or not bank_login
            ):
                raise Exception("TODO: something is not correctly set in session")

            r = requests.post(fd_backend_url, data=fd_backend_payload)

            if r.status_code == 401:
                # TAN required
                request.session["tan_challenge"] = r.json()
                redirect_dst = "/fints_downloader/import/tan/"
            elif r.status_code != 200:
                return HttpResponse(
                    content=r.content,
                    status=r.status_code,
                    content_type=r.headers["Content-Type"],
                )
            else:
                callingForm.import_data(bank_login, account, r.json())

            return HttpResponseRedirect(redirect_dst)

        context = request.context
        context["form"] = form

        return render(request, self.template_name, context)
