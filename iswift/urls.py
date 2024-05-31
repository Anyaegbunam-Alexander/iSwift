from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.static import serve
from drf_spectacular import views as doc_views
from rest_framework.routers import DefaultRouter

from core.views import CheckStatus

router = DefaultRouter()


urlpatterns = [
    re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
    re_path(r"^static/(?P<path>.*)$", serve, {"document_root": settings.STATIC_ROOT}),
    path("api/check-status/", CheckStatus.as_view()),
    path("admin/", admin.site.urls),
    path("api-auth/", include("rest_framework.urls")),
    path("api/docs/schema/", doc_views.SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/ui/", doc_views.SpectacularSwaggerView.as_view(), name="ui_docs"),
    path(
        "api/docs/redoc/", doc_views.SpectacularRedocView.as_view(url_name="schema"), name="redoc"
    ),
    path("api/auth/", include("accounts.urls"))
]

urlpatterns += router.urls
