from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin

from fints_downloader.models.account import Account
from fints_downloader.models.types import AccountTypes


class AccountListView(LoginRequiredMixin, ListView):
    template_name = "accounts.html"
    model = Account
    context_object_name = "accounts"
    # paginate_by = 10

    def get_queryset(self):
        return super().get_queryset().exclude(type=AccountTypes.FOREIGN)


class AccountView(LoginRequiredMixin, DetailView):
    template_name = "account.html"
    model = Account

    # def get_context_data(self, *args, **kwargs):
    #    context = super(AccountView, self).get_context_data(*args, **kwargs)

    #    # context['num_banks'] = Bank.objects.count()

    #    return context
