from rest_framework import serializers
from fints_downloader.models import (
    BankLogin,
    Account,
    Transaction,
    Holding,
    Tag,
    Category,
)


class BankLoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankLogin
        fields = "__all__"


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = "__all__"


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = "__all__"


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = "__all__"


class HoldingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Holding
        fields = "__all__"
