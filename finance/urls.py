from django.urls import path

from finance import views

app_name = "finance"

urlpatterns = [
    path("users/", views.ListUsers.as_view(), name="list_users"),
    path("currencies/", views.Currencies.as_view(), name="currencies"),
    path("transfer/", views.MakeTransfer.as_view(), name="transfer"),
    path("iswift-accounts/", views.iSwiftAccountsListCreateView.as_view(), name="iswift_accounts"),
]
