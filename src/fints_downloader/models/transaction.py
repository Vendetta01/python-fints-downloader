from django.db import models

# Used to generate URLs by reversing the URL patterns
from django.urls import reverse

from .basemodel import BaseModel
from .types import CurrencyTypes


class Transaction(BaseModel):
    """Model representing a transaction."""

    bk_fields = (
        "src",
        "dst",
        "amount",
        "date",
        "purpose",
    )
    src = models.ForeignKey(
        "Account",
        on_delete=models.CASCADE,
        related_name="src",
        help_text="Source account",
    )
    dst = models.ForeignKey(
        "Account",
        on_delete=models.CASCADE,
        related_name="dst",
        null=True,
        help_text="Destination account",
    )
    amount = models.DecimalField(
        max_digits=32, decimal_places=2, help_text="Transaction amount"
    )
    currency = models.CharField(
        max_length=3, choices=CurrencyTypes.choices, help_text="Currency type"
    )
    date = models.DateField(help_text="Date of transaction")
    posting_text = models.CharField(
        max_length=128, null=True, blank=True, help_text="Posting text of transaction"
    )
    purpose = models.CharField(
        max_length=1024, null=True, blank=True, help_text="Purpose of transaction"
    )
    transaction_code = models.DecimalField(
        max_digits=30,
        decimal_places=0,
        null=True,
        blank=True,
        help_text="Transaction code",
    )
    category = models.ForeignKey(
        "Category", on_delete=models.SET_NULL, null=True, help_text="Category"
    )
    tags = models.ManyToManyField("Tag", help_text="Tags")

    def get_absolute_url(self):
        """Returns the url to access a detail record for this balance."""
        return reverse("transaction", args=[str(self.id)])

    def is_categorized(self):
        return False
