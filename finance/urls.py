from django.urls import path

from finance import views

app_name = "finance"

urlpatterns = [
    path("users/", views.UsersListView.as_view(), name="list_users"),
    path("currencies/", views.CurrenciesListView.as_view(), name="currencies"),
    path("transfer/", views.MakeTransferView.as_view(), name="transfer"),
    path("iswift-accounts/", views.iSwiftAccountsListCreateView.as_view(), name="iswift_accounts"),
    path(
        "iswift-accounts/<uuid:uid>/",
        views.iSwiftAccountDetailView.as_view(),
        name="one_iswift_account",
    ),
    path(
        "transactions/<uuid:uid>/<str:type>/",
        views.TransactionDetail.as_view(),
        name="one_transaction",
    ),
]
