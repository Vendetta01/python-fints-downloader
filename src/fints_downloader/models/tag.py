from django.db import models

# Used to generate URLs by reversing the URL patterns
from django.urls import reverse

from .transaction import Transaction


class Tag(models.Model):
    """Model representing a tag."""

    name = models.CharField(max_length=1024, help_text="Tag name")
    # pattern = models.CharField(
    #    max_length=1024,
    #    help_text='Search pattern for this tag')
    # type = models.CharField(
    #    max_length=2,
    #    choices=TagTypes.choices,
    #    help_text='Type of tag')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        """Returns the url to access a detail record."""
        return reverse("tag", args=[str(self.id)])

    def get_transactions(self):
        return Transaction.objects.filter(tags__id=self.id)

    def get_sum_transactions(self):
        return (
            self.get_transactions().aggregate(sum=models.Sum("amount"))["sum"] or None
        )

    def get_count_transactions(self):
        return self.get_transactions().count()
