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
    path("admin/", admin.site.urls),
    path("api/check-status/", CheckStatus.as_view()),
    path("api-schema/", doc_views.SpectacularAPIView.as_view(), name="schema"),
    path("api-ui/", doc_views.SpectacularSwaggerView.as_view(), name="ui_docs"),
    path("api-redoc/", doc_views.SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    path('api/', include([
        path("v1/", include([
            path('drf-auth/', include('rest_framework.urls', namespace='rest_framework')),
            path("auth/", include("accounts.urls")),
            path("finance/", include("finance.urls"))
        ]))
    ]))
]

urlpatterns += router.urls
