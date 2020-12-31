from django.core.management.base import BaseCommand #, CommandError
from fints_downloader.services import FinTSService
from fints_downloader.models import Bank, BankLogin

class Command(BaseCommand):
    """Management command to update data"""
    help = 'Updates data from bank account through FinTS'

    def add_arguments(self, parser):
        # Positional arguments
        #parser.add_argument('poll_ids', nargs='+', type=int)

        # Named (optional) arguments
        parser.add_argument(
            '--interactive',
            action='store_true',
            help='Update in interactive mode',
        )

    def handle(self, *args, **options):
        for lc in BankLogin.objects.all():
            f = FinTSService(lc, options['interactive'])
            accounts = f.get_accounts()
            for account in accounts:
                # First create or update account
                account.save()
                
                # Now get balance
                balance = f.get_balance(account)
                balance.save()

                # Get transactions
                transactions = f.get_transactions(account)
                for transaction in transactions:
                    # Create foreign accounts if necessary
                    # TODO
                    transaction.save()

            self.stdout.write(self.style.SUCCESS('Successfully updated "%s"' % lc))


#        for poll_id in options['poll_ids']:
#            try:
#                poll = Poll.objects.get(pk=poll_id)
#            except Poll.DoesNotExist:
#                raise CommandError('Poll "%s" does not exist' % poll_id)
#
#            poll.opened = False
#            poll.save()
#
#            self.stdout.write(self.style.SUCCESS('Successfully closed poll "%s"' % poll_id))
