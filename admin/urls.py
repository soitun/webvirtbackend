from django.urls import include, re_path
from .views import AdminIndexView, AdminSingInView, AdminSingOutView


urlpatterns = [
    re_path("sign_in/?$", AdminSingInView.as_view(), name="admin_sign_in"),
    re_path("sign_out/?$", AdminSingOutView.as_view(), name="admin_sign_out"),

    re_path("$", AdminIndexView.as_view(), name="admin_index"),
    re_path("region/", include("admin.region.urls")),
    re_path("size/", include("admin.size.urls")),
]