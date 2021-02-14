from django.db import models

# Used to generate URLs by reversing the URL patterns
from django.urls import reverse
from datetime import date

from .transaction import Transaction


class Category(models.Model):
    """Model representing a category."""

    name = models.CharField(max_length=1024, help_text="Category name")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        """Returns the url to access a detail record."""
        return reverse("category", args=[str(self.id)])

    def _filter_date(self, mode="ltd)"):
        cur_date = date.today()
        filter_date = cur_date

        if mode.lower() == "ltd":
            filter_date = date(1, 1, 1)
        elif mode.lower() == "ytd":
            filter_date = date(cur_date.year, 1, 1)
        elif mode.lower() == "mtd":
            filter_date = date(cur_date.year, cur_date.month, 1)

        return filter_date

    def transactions(self):
        return Transaction.objects.filter(category__id=self.id)

    def sum_transactions(self, mode="ltd"):
        return (
            self.transactions()
            .filter(date__gte=self._filter_date(mode))
            .aggregate(sum=models.Sum("amount"))["sum"]
            or 0.0
        )

    def sum_transactions_ltd(self):
        return self.sum_transactions("ltd")

    def sum_transactions_ytd(self):
        return self.sum_transactions("ytd")

    def sum_transactions_mtd(self):
        return self.sum_transactions("mtd")

    def count_transactions(self, mode="ltd"):
        return self.transactions().filter(date__gte=self._filter_date(mode)).count()

    def count_transactions_ltd(self):
        return self.count_transactions("ltd")

    def count_transactions_ytd(self):
        return self.count_transactions("ytd")

    def count_transactions_mtd(self):
        return self.count_transactions("mtd")
