from django.db import models

# Used to generate URLs by reversing the URL patterns
from django.urls import reverse


# TODO: This config should be connected to a user
# Needs authorization to work...
class FinTSDownloaderBackend(models.Model):
    """Model representing the FinTS downloader backend"""

    name = models.CharField(max_length=1024, unique=True, help_text="Name of backend")
    server = models.CharField(
        max_length=1024, help_text="Server address of FinTS downloader backend"
    )
    port = models.PositiveIntegerField(
        default=80, help_text="Server port of FinTS downloader backend"
    )
    base_url = models.CharField(
        max_length=1024, blank=True, help_text="Base url of endpoint"
    )

    def get_absolute_url(self):
        """Returns the url to access a detail record for this
        fints downloader backend."""
        return reverse("fints-downloader-backend-detail", args=[str(self.id)])
