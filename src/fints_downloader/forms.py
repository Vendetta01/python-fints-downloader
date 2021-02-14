from django import forms
from django.forms import models
from django.forms.fields import MultipleChoiceField
from fints_downloader.models.account import Account
from fints_downloader.models.banklogin import BankLogin
from fints_downloader.models.transaction import Transaction
from fints_downloader.widgets import BootstrapDateTimePickerInput


class ImportAccountsForm(forms.Form):
    bank_login = forms.ModelChoiceField(
        queryset=BankLogin.objects.all(), help_text="Bank login"
    )
    # login_credentials_field = forms.ChoiceField(
    #   choices=[], help_text='TODO: help_text')

    # def __init__(self, *args, **kwargs):
    #    super(ImportForm, self).__init__(*args, **kwargs)
    #    self.fields['login_credentials_field'].choices = [
    #        (x.id, x.get_business_key()) for x in
    #           LoginCredentials.objects.all()]


class ImportAccountDetailsForm(forms.Form):
    account = forms.ModelChoiceField(
        queryset=Account.objects.filter(bank_login__isnull=False),
        help_text="Choose account as import source",
    )


class ImportHoldingsForm(ImportAccountDetailsForm):
    pass


class ImportTransactionsForm(ImportAccountDetailsForm):
    fromDate = forms.DateField(
        input_formats=["%d.%m.%Y"],
        widget=BootstrapDateTimePickerInput(),
        help_text="Beginndatum Transaktionszeitraum",
    )
    toDate = forms.DateField(
        input_formats=["%d.%m.%Y"],
        widget=BootstrapDateTimePickerInput(),
        help_text="Enddatum Transaktionszeitraum",
    )


class TANForm(forms.Form):
    tan = forms.CharField(max_length=16, help_text="TAN")


class CheckboxSelectMultipleAsTableIterator(models.ModelChoiceIterator):
    def choice(self, obj):
        return (self.field.prepare_value(obj), self.field.label_from_instance(obj), obj)


class CustomModelChoiceField(models.ModelMultipleChoiceField):
    def _get_choices(self):
        if hasattr(self, "_choices"):
            return self._choices
        return CheckboxSelectMultipleAsTableIterator(self)

    choices = property(_get_choices, MultipleChoiceField._set_choices)


class CategorizeForm(forms.Form):
    # categories are handled through FormView
    transactions = CustomModelChoiceField(
        queryset=Transaction.objects.filter(category__isnull=True).order_by("date"),
        widget=forms.CheckboxSelectMultiple,
    )

    def __init__(self, *args, **kwargs):
        self.category_text = None
        if args:
            self.category_text = args[0].get("category")
        super(CategorizeForm, self).__init__(*args, **kwargs)

    def is_valid(self):
        # run parent validation first
        valid = super(CategorizeForm, self).is_valid()

        # in case of error stop here
        if not valid:
            return valid

        if not self.category_text:
            self.add_error("category", "No category selected")
            return False

        return True
