from datetime import date, datetime
import json
import requests
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Max
from fints_downloader.models.account import Account
from fints_downloader.models.banklogin import BankLogin
from fints_downloader.models.fintsdownloaderbackend import FinTSDownloaderBackend
from fints_downloader.models.transaction import Transaction
from fints_downloader.views import importer
from fints_downloader.utils import format_backend_url, DateTimeEncoder
from backend.models import Connection, Account as BackendAccount, TransactionsIn


class Command(BaseCommand):
    """Management command to update data"""

    help = "Updates data from bank account through FinTS"

    def add_arguments(self, parser):
        # Positional arguments
        # parser.add_argument('iban', nargs='+', type=string, help='')

        # Named (optional) arguments
        parser.add_argument(
            "-i",
            "--interactive",
            action="store_true",
            help="Update in interactive mode",
        )
        parser.add_argument("-b", "--iban", help="Update this iban only")
        parser.add_argument(
            "-a", "--account_number", type=int, help="Update this account number only"
        )
        parser.add_argument(
            "-f",
            "--from_date",
            type=lambda s: datetime.strptime(s, "%Y-%m-%d"),
            help="Update from this date on",
        )
        parser.add_argument(
            "-t",
            "--to_date",
            type=lambda s: datetime.strptime(s, "%Y-%m-%d"),
            help="Update up to this date",
        )
        parser.add_argument(
            "-n", "--no_dates", action="store_true", help="Update without date values"
        )

    def handle(self, *args, **options):
        interactive = options.get("interactive")
        iban = options.get("iban")
        account_number = options.get("account_number")
        from_date = options.get("from_date")
        to_date = options.get("to_date")
        no_dates = options.get("no_dates")

        if iban:
            # Update this iban only
            account = Account.objects.filter(iban=iban).first()
            if not account:
                raise CommandError(f"IBAN '{iban}' does not exist!")
            elif not account.bank_login:
                raise CommandError(f"IBAN '{iban}' has no login credentials!")
            self._update_account(account, interactive)
        elif account_number:
            # Update this account number only
            account = Account.objects.filter(number=account_number).first()
            if not account:
                raise CommandError(
                    (f"Account number '{account_number}' " "does not exist!")
                )
            elif not account.bank_login:
                raise CommandError(
                    (f"Account number '{account_number}' " "has no login credentials!")
                )
            self._update_account(account, interactive)
        else:
            # Update all accounts
            for bank_login in BankLogin.objects.all():
                for account in Account.objects.filter(bank_login=bank_login):
                    self._update_account(
                        account, interactive, no_dates, from_date, to_date
                    )

    def _update_account(
        self, account, interactive, no_dates, from_date=None, to_date=None
    ):
        if not account.bank_login.enabled:
            self.stdout.write(
                self.style.WARNING(f"Account '{account}' is disabled, ignoring...")
            )
            return
        elif account.bank_login.tan_required:
            if interactive:
                account.bank_login.refresh_from_db()
                account.bank_login.tan_required = False
                account.bank_login.save()
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"Account '{account}' requires user interaction, ignoring..."
                    )
                )
                return

        # Update account
        if no_dates:
            from_date = None
            to_date = None
        else:
            if not from_date:
                # year needs to be 1000, otherwise backend (fints)
                # produces error (bug?)
                from_date = (
                    Transaction.objects.filter(src=account)
                    .aggregate(Max("date"))
                    .get("date_max", date(1000, 1, 1))
                )
            if not to_date:
                to_date = date.today()

        fd_backend_url = format_backend_url(
            FinTSDownloaderBackend.objects.first(), "transactions"
        )

        backend_connection = Connection(
            user_id=account.bank_login.user_id,
            pin=account.bank_login.password,
            server=account.bank_login.server,
            bank_identifier=account.bank_login.code,
            tan_mechanism=account.bank_login.tan_mechanism,
        )
        backend_account = BackendAccount(
            name=account.name,
            iban=account.iban,
            accountnumber=account.number,
            bic=account.bic,
        )
        fd_backend_payload = json.dumps(
            TransactionsIn(
                connection=backend_connection,
                account=backend_account,
                fromDate=from_date,
                toDate=to_date,
            ).dict(),
            cls=DateTimeEncoder,
        )

        r = requests.post(fd_backend_url, data=fd_backend_payload)

        if r.status_code == 401:
            # TAN required
            if not interactive:
                account.bank_login.refresh_from_db()
                account.bank_login.tan_required = True
                account.bank_login.save()
                raise CommandError(f"TAN required for account '{account}'")
            else:
                account.bank_login.refresh_from_db()
                account.bank_login.tan_required = False
                account.bank_login.save()
                tan = input(r.json())

                fd_backend_payload = json.dumps(
                    json.loads(fd_backend_payload).update({"tan": tan}),
                    cls=DateTimeEncoder,
                )

                r = requests.post(fd_backend_url, data=fd_backend_payload)

                if r.status_code == 401:
                    account.bank_login.refresh_from_db()
                    account.bank_login.tan_required = True
                    account.bank_login.save()
                    raise CommandError(f"TAN required for account '{account}'")

        if r.status_code != 200:
            raise CommandError(f"Error during backend call: {r.status_code}")

        # If all went well import data
        importer.ImportTransactionsView().import_data(
            account.bank_login, account, r.json()
        )

        self.stdout.write(
            self.style.SUCCESS(f"Account '{account}' successfully updated.")
        )
