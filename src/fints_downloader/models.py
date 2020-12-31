from django.db import models
from django.db.models import Q, Sum
# Used to generate URLs by reversing the URL patterns
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from hashlib import sha256
from datetime import datetime, timedelta


# TODO: This config should be connected to a user
# Needs authorization to work...
class FinTSDownloaderBackend(models.Model):
    """Model representing the FinTS downloader backend"""
    name = models.CharField(
        max_length=1024,
        unique=True,
        help_text='Name of backend')
    server = models.CharField(
        max_length=1024,
        help_text='Server address of FinTS downloader backend')
    port = models.PositiveIntegerField(
        default=80,
        help_text='Server port of FinTS downloader backend')
    base_url = models.CharField(
        max_length=1024,
        blank=True,
        help_text='Base url of endpoint')

    def get_absolute_url(self):
        """Returns the url to access a detail record for this
        fints downloader backend."""
        return reverse('fints-downloader-backend-detail', args=[str(self.id)])


class Category(models.Model):
    """Model representing a category."""
    name = models.CharField(
        max_length=1024,
        help_text='Category name')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        """Returns the url to access a detail record."""
        return reverse('category', args=[str(self.id)])


class Tag(models.Model):
    """Model representing a tag."""
    name = models.CharField(
        max_length=1024,
        help_text='Tag name')
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
        return reverse('tag', args=[str(self.id)])

    def get_transactions(self):
        return Transaction.objects.filter(tags__id=self.id)

    def get_sum_transactions(self):
        return self.get_transactions().aggregate(
            sum=models.Sum('amount'))['sum'] or None

    def get_count_transactions(self):
        return self.get_transactions().count()


class CurrencyTypes(models.TextChoices):
    """Model representing different currencies."""
    EURO = 'EUR', _('Euro')


class AccountTypes(models.TextChoices):
    """Model representing different account types."""
    CHECKING = 'ch', _('checking')
    CREDIT_CARD = 'cc', _('credit card')
    DEPOT = 'dp', _('depot')
    FOREIGN = 'fg', _('foreign')


class TagTypes(models.TextChoices):
    """Model representing different tag types."""
    CATEGORY = 'ct', _('Category')
    OTHER = 'ot', _('Other')


class BaseModel(models.Model):
    """Class containing all common fields"""
    ID_MAX_LENGTH = 64

    bk_fields = ()

    id = models.CharField(
        max_length=ID_MAX_LENGTH,
        help_text='ID containing the hashed business key',
        primary_key=True)
    bk_id = models.CharField(
        max_length=1024, help_text='Unhashed business key'
    )
    last_update = models.DateTimeField(
        help_text='Last update timestamp', auto_now=True)

    class Meta:
        abstract = True
        ordering = ['bk_id']

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
        return sha256(str(self.get_business_key()
                          ).encode('utf-8')).hexdigest()

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


class BankLogin(BaseModel):
    """Model representing login credentials for a specific bank"""
    bk_fields = ('code', 'user_id',)
    name = models.CharField(
        max_length=1024,
        null=True,
        blank=True,
        help_text='Decribing name of credentials')
    user_id = models.CharField(
        max_length=1024,
        help_text='Login/user name')
    password = models.CharField(
        max_length=1024,
        help_text='Password or pin for this account')
    tan_mechanism = models.CharField(
        max_length=3,
        null=True,
        blank=True,
        help_text='Default TAN mechanism')
    bic = models.CharField(
        max_length=11,
        help_text='Bank identifier code')
    code = models.DecimalField(
        max_digits=8,
        decimal_places=0,
        help_text='German bank code')
    server = models.CharField(
        max_length=1024,
        help_text='Bank fints server connection string')

    def get_absolute_url(self):
        """Returns the url to access a detail record for these login
        credetinals."""
        return reverse('bank-login-detail', args=[str(self.id)])


class Account(BaseModel):
    """Model representing an account"""
    bk_fields = ('number', 'bic')
    bank_login = models.ForeignKey(
        BankLogin,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text='Login credentials used for this account')
    iban = models.CharField(
        max_length=34,
        null=True,
        blank=True,
        help_text='IBAN')
    number = models.DecimalField(
        max_digits=30,
        decimal_places=0,
        help_text='Account number')
    bic = models.CharField(
        max_length=11,
        null=True,
        blank=True,
        help_text='Bank identifier code')
    type = models.CharField(
        max_length=2,
        choices=AccountTypes.choices,
        help_text='Type of account')
    name = models.CharField(
        max_length=256,
        help_text='Account name',
        null=True,
        blank=True)
    init_balance = models.DecimalField(
        max_digits=32,
        decimal_places=2,
        default=0,
        help_text='Initial account balance')

    def get_absolute_url(self):
        """Returns the url to access a detail record for this account."""
        return reverse('account', args=[str(self.id)])

    def get_current_balance(self):
        # TODO: calculate balance from transactions and init value
        bal = Balance.objects.filter(account_id=self.id).order_by(
            '-valid_datetime').first()
        if not bal:
            return '-'

        # return f"{bal.amount} {bal.currency}"
        return bal.amount

    def sum_transactions(self, fromDate=None, toDate=None, add_filter=None):
        obj_filter = Q(src=self)
        if fromDate:
            obj_filter = obj_filter & Q(date__gte=fromDate)
        if toDate:
            obj_filter = obj_filter & Q(date__lte=toDate)
        if add_filter:
            obj_filter = obj_filter & add_filter
        sum = Transaction.objects.filter(
            obj_filter
        ).aggregate(sum=Sum('amount'))['sum'] or 0
        return self.init_balance + sum

    def get_spending_cur_month(self):
        today = datetime.today()
        return self.sum_transactions(
            fromDate=today.replace(day=1),
            toDate=today,
            add_filter=Q(amount__lt=0))

    def get_spending_last_month(self):
        last_month = datetime.today().replace(day=1) - \
            timedelta(days=1)
        return self.sum_transactions(
            fromDate=last_month.replace(day=1),
            toDate=last_month,
            add_filter=Q(amount__lt=0))

    def get_change_last_month(self):
        last_month = datetime.today().replace(day=1) - \
            timedelta(days=1)
        return self.sum_transactions(
            fromDate=last_month.replace(day=1),
            toDate=last_month)


class Balance(BaseModel):
    """Model representing an account balance."""
    bk_fields = ('account', 'valid_datetime',)
    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        help_text='Account which the balance belongs to')
    amount = models.DecimalField(
        max_digits=32,
        decimal_places=2,
        help_text='Account balance')
    currency = models.CharField(
        max_length=3,
        choices=CurrencyTypes.choices,
        help_text='Currency type')
    valid_datetime = models.DateTimeField(
        help_text='Timestamp at which this balance was valid')

    def get_absolute_url(self):
        """Returns the url to access a detail record for this balance."""
        return reverse('balance-detail', args=[str(self.id)])


class Transaction(BaseModel):
    """Model representing a transaction."""
    bk_fields = ('src', 'dst', 'amount', 'date', 'purpose',)
    src = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name='src',
        help_text='Source account')
    dst = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name='dst',
        null=True,
        help_text='Destination account')
    amount = models.DecimalField(
        max_digits=32,
        decimal_places=2,
        help_text='Transaction amount')
    currency = models.CharField(
        max_length=3,
        choices=CurrencyTypes.choices,
        help_text='Currency type')
    date = models.DateField(
        help_text='Date of transaction')
    posting_text = models.CharField(
        max_length=128,
        null=True,
        blank=True,
        help_text='Posting text of transaction')
    purpose = models.CharField(
        max_length=1024,
        null=True,
        blank=True,
        help_text='Purpose of transaction')
    transaction_code = models.DecimalField(
        max_digits=30,
        decimal_places=0,
        null=True,
        blank=True,
        help_text='Transaction code')
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        help_text='Category')
    tags = models.ManyToManyField(
        Tag,
        help_text='Tags')

    def get_absolute_url(self):
        """Returns the url to access a detail record for this balance."""
        return reverse('transaction', args=[str(self.id)])

    def is_categorized(self):
        return False


class Holding(BaseModel):
    """Model rerpesenting a holding."""
    bk_fields = ('account', 'isin')
    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        help_text='Account which the holding belongs to')
    isin = models.TextField(
        max_length=12,
        help_text='ISIN')
    wkn = models.TextField(
        max_length=6,
        null=True,
        blank=True,
        help_text='German Wertpapierkennnummer')
    name = models.TextField(
        max_length=256,
        help_text='Name')
    market_value = models.DecimalField(
        max_digits=32,
        decimal_places=2,
        help_text='Market value')
    currency = models.CharField(
        max_length=3,
        choices=CurrencyTypes.choices,
        help_text='Currency type')
    valuation_date = models.DateField(
        help_text='Valuation date')
    pieces = models.PositiveIntegerField(
        help_text='Number of pieces')
    total_value = models.DecimalField(
        max_digits=32,
        decimal_places=2,
        help_text='Total value')
    acquisitionprice = models.DecimalField(
        max_digits=32,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Acquisition price')

    def get_absolute_url(self):
        """Returns the url to access a detail record for this holding."""
        return reverse('holding-detail', args=[str(self.id)])
