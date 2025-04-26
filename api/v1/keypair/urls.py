from django.urls import re_path

from keypair.views import KeyPairDataAPI, KeyPairListAPI

urlpatterns = [
    re_path(r"$", KeyPairListAPI.as_view(), name="keypair_list_api"),
    re_path(r"(?P<pk>\d+)/?$", KeyPairDataAPI.as_view(), name="keypair_data_api"),
]
