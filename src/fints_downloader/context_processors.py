from fints_downloader.models.account import Account
from fints_downloader.models.banklogin import BankLogin
from fints_downloader.models.category import Category
from fints_downloader.models.holding import Holding
from fints_downloader.models.tag import Tag
from fints_downloader.models.transaction import Transaction
from fints_downloader.models.types import AccountTypes


def get_default_context(request):
    return {
        "counts": {
            "accounts": Account.objects.exclude(type=AccountTypes.FOREIGN).count(),
            "bank_logins": BankLogin.objects.count(),
            "transactions": Transaction.objects.count(),
            "transactions_uncategorized": Transaction.objects.filter(
                category__isnull=True
            ).count(),
            "holdings": Holding.objects.count(),
            "tags": Tag.objects.count(),
            "categories": Category.objects.count(),
        }
    }
