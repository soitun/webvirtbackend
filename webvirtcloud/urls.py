"""
WebVirtCloud URL Configuration
"""
from django.conf import settings
from django.urls import include, path, re_path
from webvirtcloud.views import exception_handler404, exception_handler500


handler404 = exception_handler404
handler500 = exception_handler500


urlpatterns = [
    re_path(r"", include("singlepage.urls")),
    re_path(r"account/", include("account.urls")),
    re_path(r"api/", include("api.urls")),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        path("__debug__/", include("debug_toolbar.urls")),
    ]
