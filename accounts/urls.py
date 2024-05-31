from django.urls import path

from accounts import views

app_name = "accounts"

urlpatterns = [
    path("signup/", views.SignUpView.as_view(), name="sign_up"),
]
