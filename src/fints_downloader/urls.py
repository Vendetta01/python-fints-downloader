from django.urls import path

# from rest_framework.urlpatterns import format_suffix_patterns

from fints_downloader.views import (
    models,
    index,
    account,
    tag,
    importer,
    transaction,
    category,
    balance,
)


urlpatterns = [
    path("banklogins/", models.BankLoginList.as_view()),
    path("banklogins/<str:pk>/", models.BankLoginDetail.as_view()),
    path("transactions/", transaction.TransactionList.as_view(), name="transactions"),
    path(
        "transactions/categorize/",
        transaction.Categorize.as_view(),
        name="transactions_categorize",
    ),
    path(
        "transaction/<str:pk>/",
        transaction.TransactionDetail.as_view(),
        name="transaction",
    ),
    path("categories/", category.CategoryList.as_view(), name="categories"),
    path("category/<str:pk>/", category.CategoryDetail.as_view(), name="category"),
    path("", index.IndexView.as_view(), name="index"),
    path("balance/<str:pk>/", balance.BalanceLineChartJSON.as_view(), name="balance"),
    path("accounts/", account.AccountListView.as_view(), name="accounts"),
    path("account/<str:pk>", account.AccountView.as_view(), name="account"),
    path("tags/", tag.TagListView.as_view(), name="tags"),
    path("tag/<str:pk>", tag.TagView.as_view(), name="tag"),
    path(
        "import/accounts/",
        importer.ImportAccountsView.as_view(),
        name="import_accounts",
    ),
    path(
        "import/transactions/",
        importer.ImportTransactionsView.as_view(),
        name="import_transactions",
    ),
    path(
        "import/holdings/",
        importer.ImportHoldingsView.as_view(),
        name="import_holdings",
    ),
    path("import/tan/", importer.TANView.as_view(), name="import_tan"),
]

# urlpatterns = format_suffix_patterns(urlpatterns)
