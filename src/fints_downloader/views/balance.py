from chartjs.views.lines import BaseLineChartView
from django.db.models import Sum

from fints_downloader.models import Account, Transaction


class BalanceLineChartJSON(BaseLineChartView):
    def get_providers(seld):
        return ['Balance']

    def get_labels(self):
        """Return 7 labels for the x-axis."""
        transactions = Transaction.objects.filter(
            src__id=self.kwargs.get('pk')).values('date').annotate(
            Sum('amount')).order_by('date')
        labels = []
        for transaction in transactions:
            labels.append(transaction['date'])
        return labels
        # return ["January", "February", "March", "April", "May", "June", "July"]

    # def get_providers(self):
    #    """Return names of datasets."""
    #    return ["Central", "Eastside", "Westside"]

    def get_data(self):
        """Return 3 datasets to plot."""
        transactions = Transaction.objects.filter(
            src__id=self.kwargs.get('pk')).values('date').annotate(
            Sum('amount')).order_by('date')
        init_balance = Account.objects.filter(
            pk=self.kwargs.get('pk')).first().init_balance
        # do something and convert to ...
        data = []
        last_amount = init_balance
        for transaction in transactions:
            last_amount += transaction['amount__sum']
            data.append(last_amount)
        return [data]
