from django.db import models
from hashlib import sha256


class BaseModel(models.Model):
    """Class containing all common fields"""

    ID_MAX_LENGTH = 64

    bk_fields = ()

    id = models.CharField(
        max_length=ID_MAX_LENGTH,
        help_text="ID containing the hashed business key",
        primary_key=True,
    )
    bk_id = models.CharField(max_length=1024, help_text="Unhashed business key")
    last_update = models.DateTimeField(help_text="Last update timestamp", auto_now=True)

    class Meta:
        abstract = True
        ordering = ["bk_id"]

    def __str__(self):
        return self.get_business_key()

    def save(self, *args, **kwargs):  # pylint: disable=signature-differs
        # if self._state.adding or self.id is None:
        #    self.id = self.get_hash_id()
        # TODO: sanitation logic to convert all field values to db field values
        if self.id is None:
            self.bk_id = self.get_business_key()
            self.id = self.get_hash_id()
        super(BaseModel, self).save(*args, **kwargs)

    def get_hash_id(self):
        return sha256(str(self.get_business_key()).encode("utf-8")).hexdigest()

    def get_business_key(self):
        """Create string representation from business key field list."""
        unformated_bk = ""
        values_list = []
        for key in self.bk_fields[:-1]:
            unformated_bk += "{}_"
            values_list.append(getattr(self, key))
        if len(self.bk_fields) > 0:
            unformated_bk += "{}"
            values_list.append(getattr(self, self.bk_fields[-1]))

        return unformated_bk.format(*values_list)
