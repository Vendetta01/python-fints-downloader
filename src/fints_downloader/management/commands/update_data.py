from django.core.management.base import BaseCommand, CommandError
from fints_downloader.models import BankLogin, Account


class Command(BaseCommand):
    """Management command to update data"""
    help = 'Updates data from bank account through FinTS'

    def add_arguments(self, parser):
        # Positional arguments
        # parser.add_argument('iban', nargs='+', type=string, help='')

        # Named (optional) arguments
        parser.add_argument(
            '-i',
            '--interactive',
            action='store_true',
            help='Update in interactive mode',
        )
        parser.add_argument(
            '-b',
            '--iban',
            help='Update this iban only'
        )
        parser.add_argument(
            '-n',
            '--account_number',
            type=int,
            help='Update this account number only'
        )

    def handle(self, *args, **options):
        interactive = options.get('interactive')
        iban = options.get('iban')
        account_number = options.get('account_number')

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
                raise CommandError((f"Account number '{account_number}' "
                    "does not exist!"))
            elif not account.bank_login:
                raise CommandError((f"Account number '{account_number}' "
                    "has no login credentials!"))
            self._update_account(account, interactive)
        else:
            # Update all accounts
            for bank_login in BankLogin.objects.all():
                for account in Account.objects.filter(bank_login=bank_login):
                    self._update_account(account, interactive)

    def _update_account(self, account, interactive):
        if not account.bank_login.enabled:
            self.stdout.write(self.style.WARNING(
                f"Account '{account}' is disabled, ignoring..."))
            return
        elif account.bank_login.tan_required:
            self.stdout.write(self.style.WARNING(
                f"Account '{account}' requires user interaction, ignoring..."))
            return

        # Update account
        raise Exception("Not implemented yet")
        # TODO:
        # -> extract max transaction date
        # -> post request on import/transaction
        # -> extract result from response (where are we redirected to?)
        self.stdout.write(self.style.SUCCESS(
            f"Account '{account}' successfully updated."))
