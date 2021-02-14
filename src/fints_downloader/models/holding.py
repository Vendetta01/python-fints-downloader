from django.db import models

# Used to generate URLs by reversing the URL patterns
from django.urls import reverse

from .basemodel import BaseModel
from .types import CurrencyTypes


class Holding(BaseModel):
    """Model rerpesenting a holding."""

    bk_fields = ("account", "isin")
    account = models.ForeignKey(
        "Account",
        on_delete=models.CASCADE,
        help_text="Account which the holding belongs to",
    )
    isin = models.TextField(max_length=12, help_text="ISIN")
    wkn = models.TextField(
        max_length=6, null=True, blank=True, help_text="German Wertpapierkennnummer"
    )
    name = models.TextField(max_length=256, help_text="Name")
    market_value = models.DecimalField(
        max_digits=32, decimal_places=2, help_text="Market value"
    )
    currency = models.CharField(
        max_length=3, choices=CurrencyTypes.choices, help_text="Currency type"
    )
    valuation_date = models.DateField(help_text="Valuation date")
    pieces = models.PositiveIntegerField(help_text="Number of pieces")
    total_value = models.DecimalField(
        max_digits=32, decimal_places=2, help_text="Total value"
    )
    acquisitionprice = models.DecimalField(
        max_digits=32,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Acquisition price",
    )

    def get_absolute_url(self):
        """Returns the url to access a detail record for this holding."""
        return reverse("holding-detail", args=[str(self.id)])
