from django.contrib import admin
from django.urls import path
from core.views import CheckStatus


urlpatterns = [
    path("admin/", admin.site.urls),
    path("check-status/", CheckStatus.as_view()),
]
