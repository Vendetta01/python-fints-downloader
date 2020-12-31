from django.views.generic import ListView, DetailView, FormView
from django.http import HttpResponseRedirect
from django.shortcuts import render

from fints_downloader.models import Transaction, Category
from fints_downloader.forms import CategorizeForm


class TransactionList(ListView):
    template_name = 'transactions.html'
    model = Transaction
    context_object_name = 'transactions'
    # paginate_by = 10

    # def get_queryset(self):
    #    return super().get_queryset().exclude(type=AccountTypes.FOREIGN)


class TransactionDetail(DetailView):
    template_name = 'transaction.html'
    model = Transaction

    # def get_context_data(self, *args, **kwargs):
    #    context = super(AccountView, self).get_context_data(*args, **kwargs)

    #    # context['num_banks'] = Bank.objects.count()

    #    return context


class Categorize(FormView):
    template_name = 'categorize.html'
    form_class = CategorizeForm
    success_url = '/fints_downloader/transactions/categorize/'
    # context_object_name = 'accounts'
    # paginate_by = 10

    # def get_queryset(self):
    #    return super().get_queryset().exclude(type=AccountTypes.FOREIGN)

    def post(self, request, *args, **kwargs):
        form = CategorizeForm(request.POST)
        if form.is_valid():
            transactions = form.cleaned_data['transactions']

            # check if category exists and create otherwise
            category = None
            try:
                category = Category.objects.get(name=form.category_text)
            except Category.DoesNotExist:
                category = Category.objects.create(name=form.category_text)

            for transaction in transactions:
                # Make sure we get the current version
                category.refresh_from_db()
                transaction.refresh_from_db()
                transaction.category = category
                transaction.save()
            return HttpResponseRedirect(self.success_url)

        context = {}
        if hasattr(context, 'request'):
            context = request.context
        context['form'] = form
        return render(request, self.template_name, context)

    def get_context_data(self, *args, **kwargs):
        context = super(Categorize, self).get_context_data(*args, **kwargs)

        # transactions are handled through form
        # context['transactions'] = Transaction.objects.filter(
        #    category__isnull=True).order_by('date')
        context['categories'] = Category.objects.all()

        return context
