from django.contrib import admin
from fints_downloader.models import BankLogin, Account, \
    Transaction, Holding, FinTSDownloaderBackend, Category, Tag


@admin.register(FinTSDownloaderBackend)
class FinTSDownloaderBackendAdmin(admin.ModelAdmin):
    list_display = ('name', 'server', 'port', 'base_url')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)


class BaseModelAdmin(admin.ModelAdmin):
    readonly_fields = ('id', 'bk_id', 'last_update')
    editableonly_on_creation_fields = ()
    list_display = ('bk_id',)

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + self.editableonly_on_creation_fields
        return self.readonly_fields


@admin.register(BankLogin)
class BankLoginAdmin(BaseModelAdmin):
    list_display = BaseModelAdmin.list_display + ('name', 'user_id', 'code')
    list_filter = ('code',)
    editableonly_on_creation_fields = BankLogin.bk_fields


@admin.register(Account)
class AccountAdmin(BaseModelAdmin):
    list_display = BaseModelAdmin.list_display + (
        'name', 'type', 'number', 'iban', 'bic', 'bank_login')
    list_filter = ('type', 'bank_login')
    editableonly_on_creation_fields = Account.bk_fields


@admin.register(Transaction)
class TransactionAdmin(BaseModelAdmin):
    list_display = BaseModelAdmin.list_display + \
        ('date', 'amount', 'currency', 'purpose', 'src', 'dst')
    list_filter = ('date', 'src', 'dst')
    editableonly_on_creation_fields = Transaction.bk_fields


@admin.register(Holding)
class HoldingAdmin(BaseModelAdmin):
    list_display = BaseModelAdmin.list_display + \
        ('name', 'isin', 'pieces', 'total_value', 'account')
    list_filter = ('name', 'isin', 'account')
    editableonly_on_creation_fields = Holding.bk_fields
