from django.urls import re_path

from .views import AdminUserBillingView, AdminUserCreateView, AdminUserDataView, AdminUserIndexView, AdminUserUpdateView

urlpatterns = [
    re_path(r"$", AdminUserIndexView.as_view(), name="admin_user_index"),
    re_path(r"create/?$", AdminUserCreateView.as_view(), name="admin_user_create"),
    re_path(r"^(?P<pk>\d+)/$", AdminUserDataView.as_view(), name="admin_user_data"),
    re_path(r"^(?P<pk>\d+)/billing/$", AdminUserBillingView.as_view(), name="admin_user_billing"),
    re_path(r"^(?P<pk>\d+)/update/?$", AdminUserUpdateView.as_view(), name="admin_user_update"),
]
