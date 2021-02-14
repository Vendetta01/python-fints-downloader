from django.db import models

# Used to generate URLs by reversing the URL patterns
from django.urls import reverse

from .basemodel import BaseModel


class BankLogin(BaseModel):
    """Model representing login credentials for a specific bank"""

    bk_fields = (
        "code",
        "user_id",
    )
    name = models.CharField(
        max_length=1024,
        null=True,
        blank=True,
        help_text="Decribing name of credentials",
    )
    user_id = models.CharField(max_length=1024, help_text="Login/user name")
    password = models.CharField(
        max_length=1024, help_text="Password or pin for this account"
    )
    tan_mechanism = models.CharField(
        max_length=3, null=True, blank=True, help_text="Default TAN mechanism"
    )
    bic = models.CharField(max_length=11, help_text="Bank identifier code")
    code = models.DecimalField(
        max_digits=8, decimal_places=0, help_text="German bank code"
    )
    server = models.CharField(
        max_length=1024, help_text="Bank fints server connection string"
    )
    enabled = models.BooleanField(default=True, help_text="Is this bank login enabled")
    tan_required = models.BooleanField(
        default=False, help_text="Last automatic access required a TAN"
    )

    def get_absolute_url(self):
        """Returns the url to access a detail record for these login
        credetinals."""
        return reverse("bank-login-detail", args=[str(self.id)])
