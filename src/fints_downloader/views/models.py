from rest_framework import generics
from fints_downloader.models.account import Account
from fints_downloader.models.banklogin import BankLogin
from fints_downloader.models.holding import Holding
from fints_downloader.models.transaction import Transaction
from fints_downloader.serializers import (
    BankLoginSerializer,
    AccountSerializer,
    TransactionSerializer,
    HoldingSerializer,
)


class BankLoginList(generics.ListCreateAPIView):
    queryset = BankLogin.objects.all()
    serializer_class = BankLoginSerializer


class BankLoginDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = BankLogin.objects.all()
    serializer_class = BankLoginSerializer


class AccountList(generics.ListCreateAPIView):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer


class AccountDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer


class TransactionList(generics.ListCreateAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer


class TransactionDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer


class HoldingList(generics.ListCreateAPIView):
    queryset = Holding.objects.all()
    serializer_class = HoldingSerializer


class HoldingDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Holding.objects.all()
    serializer_class = HoldingSerializer
