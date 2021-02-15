from rest_framework import generics
from django.contrib.auth.mixins import LoginRequiredMixin
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


class BankLoginList(LoginRequiredMixin, generics.ListCreateAPIView):
    queryset = BankLogin.objects.all()
    serializer_class = BankLoginSerializer


class BankLoginDetail(LoginRequiredMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = BankLogin.objects.all()
    serializer_class = BankLoginSerializer


class AccountList(LoginRequiredMixin, generics.ListCreateAPIView):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer


class AccountDetail(LoginRequiredMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer


class TransactionList(LoginRequiredMixin, generics.ListCreateAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer


class TransactionDetail(LoginRequiredMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer


class HoldingList(LoginRequiredMixin, generics.ListCreateAPIView):
    queryset = Holding.objects.all()
    serializer_class = HoldingSerializer


class HoldingDetail(LoginRequiredMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = Holding.objects.all()
    serializer_class = HoldingSerializer
