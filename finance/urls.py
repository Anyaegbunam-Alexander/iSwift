from django.urls import path

from finance import views

app_name = "finance"

urlpatterns = [
    path("users/", views.ListUsers.as_view(), name="list_users"),
]
