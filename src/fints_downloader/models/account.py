from django.db import models
from django.db.models import Q, Sum

# Used to generate URLs by reversing the URL patterns
from django.urls import reverse
from datetime import timedelta, datetime

from .basemodel import BaseModel
from .types import AccountTypes
from .transaction import Transaction


class Account(BaseModel):
    """Model representing an account"""

    bk_fields = ("number", "bic")
    bank_login = models.ForeignKey(
        "BankLogin",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Login credentials used for this account",
    )
    iban = models.CharField(max_length=34, null=True, blank=True, help_text="IBAN")
    number = models.DecimalField(
        max_digits=30, decimal_places=0, help_text="Account number"
    )
    bic = models.CharField(
        max_length=11, null=True, blank=True, help_text="Bank identifier code"
    )
    type = models.CharField(
        max_length=2, choices=AccountTypes.choices, help_text="Type of account"
    )
    name = models.CharField(
        max_length=256, help_text="Account name", null=True, blank=True
    )
    init_balance = models.DecimalField(
        max_digits=32, decimal_places=2, default=0, help_text="Initial account balance"
    )

    def get_absolute_url(self):
        """Returns the url to access a detail record for this account."""
        return reverse("account", args=[str(self.id)])

    def get_current_balance(self):
        return self.sum_transactions()

    def sum_transactions(self, fromDate=None, toDate=None, add_filter=None):
        obj_filter = Q(src=self)
        if fromDate:
            obj_filter = obj_filter & Q(date__gte=fromDate)
        if toDate:
            obj_filter = obj_filter & Q(date__lte=toDate)
        if add_filter:
            obj_filter = obj_filter & add_filter
        sum = (
            Transaction.objects.filter(obj_filter).aggregate(sum=Sum("amount"))["sum"]
            or 0
        )
        return self.init_balance + sum

    def get_spending_cur_month(self):
        today = datetime.today()
        return self.sum_transactions(
            fromDate=today.replace(day=1), toDate=today, add_filter=Q(amount__lt=0)
        )

    def get_spending_last_month(self):
        last_month = datetime.today().replace(day=1) - timedelta(days=1)
        return self.sum_transactions(
            fromDate=last_month.replace(day=1),
            toDate=last_month,
            add_filter=Q(amount__lt=0),
        )

    def get_change_last_month(self):
        last_month = datetime.today().replace(day=1) - timedelta(days=1)
        return self.sum_transactions(
            fromDate=last_month.replace(day=1), toDate=last_month
        )
