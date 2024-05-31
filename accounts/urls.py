from django.urls import path

from accounts import views

app_name = "accounts"

urlpatterns = [
    path("signup/", views.SignUpView.as_view(), name="signup"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("verify-otp/", views.VerifyOTPView.as_view(), name="verify_otp"),
    path("regenerate-otp/", views.RegenerateOTPViewSignup.as_view(), name="regenerate_otp"),
    path(
        "password-reset/get-otp/",
        views.GenerateOTPForPasswordReset.as_view(),
        name="password_reset_get_otp",
    ),
    path(
        "password-reset/verify-otp/",
        views.VerifyOTPPasswordReset.as_view(),
        name="password_reset_verify_otp",
    ),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path(
        "password-reset/from-otp/",
        views.ResetPasswordFromOTP.as_view(),
        name="reset_password_from_otp",
    ),
    path("password-reset/", views.AuthUserResetPasswordView.as_view(), name="password_reset"),
]
