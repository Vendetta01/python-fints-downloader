from django.db import models

# Used to generate URLs by reversing the URL patterns
from django.utils.translation import gettext_lazy as _


class CurrencyTypes(models.TextChoices):
    """Model representing different currencies."""

    EURO = "EUR", _("Euro")


class AccountTypes(models.TextChoices):
    """Model representing different account types."""

    CHECKING = "ch", _("checking")
    CREDIT_CARD = "cc", _("credit card")
    DEPOT = "dp", _("depot")
    FOREIGN = "fg", _("foreign")


class TagTypes(models.TextChoices):
    """Model representing different tag types."""

    CATEGORY = "ct", _("Category")
    OTHER = "ot", _("Other")
