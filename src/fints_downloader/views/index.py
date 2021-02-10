from django.views.generic import TemplateView

# from fints_downloader.models import BankLogin, Account, Transaction, Holding


class IndexView(TemplateView):
    template_name = "index.html"

    # def get_context_data(self, *args, **kwargs):
    #    context = super(IndexView, self).get_context_data(*args, *kwargs)

    #    context['num_logins'] = BankLogin.objects.count()
    #    context['accounts'] = {'count': Account.objects.count()}
    #    context['transactions'] = {'count': Transaction.objects.count()}
    #    context['holdings'] = {'count': Holding.objects.count()}

    #    return context
