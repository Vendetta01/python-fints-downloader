from fints_downloader.models import BankLogin, Account, Transaction, Holding,\
    Tag, Category, AccountTypes


def get_default_context(request):
    return {
        'counts': {
            'accounts':
                Account.objects.exclude(type=AccountTypes.FOREIGN).count(),
            'bank_logins': BankLogin.objects.count(),
            'transactions': Transaction.objects.count(),
            'transactions_uncategorized':
                Transaction.objects.filter(category__isnull=True).count(),
            'holdings': Holding.objects.count(),
            'tags': Tag.objects.count(),
            'categories': Category.objects.count()
        }
    }
