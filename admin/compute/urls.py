from django.urls import re_path

from .views import (
    AdminComputeCreateView,
    AdminComputeDeleteView,
    AdminComputeIndexView,
    AdminComputeNetworkCreateView,
    AdminComputeNetworkDeleteView,
    AdminComputeNetworksView,
    AdminComputeNetworkView,
    AdminComputeNwfilterCreateView,
    AdminComputeNwfilterDeleteView,
    AdminComputeNwfiltersView,
    AdminComputeNwfilterView,
    AdminComputeOverviewView,
    AdminComputeSecretCreateView,
    AdminComputeSecretDeleteView,
    AdminComputeSecretsView,
    AdminComputeSecretValueView,
    AdminComputeStorageDeleteView,
    AdminComputeStorageDirCreateView,
    AdminComputeStorageRBDCreateView,
    AdminComputeStoragesView,
    AdminComputeStorageView,
    AdminComputeStorageVolumeCloneView,
    AdminComputeStorageVolumeCreateView,
    AdminComputeStorageVolumeDeleteView,
    AdminComputeStorageVolumeResizeView,
    AdminComputeUpdateView,
)

urlpatterns = [
    re_path(r"$", AdminComputeIndexView.as_view(), name="admin_compute_index"),
    re_path(r"create/?$", AdminComputeCreateView.as_view(), name="admin_compute_create"),
    re_path(r"update/(?P<pk>\d+)/?$", AdminComputeUpdateView.as_view(), name="admin_compute_update"),
    re_path(r"delete/(?P<pk>\d+)/?$", AdminComputeDeleteView.as_view(), name="admin_compute_delete"),
    re_path(r"(?P<pk>\d+)/overview/?$", AdminComputeOverviewView.as_view(), name="admin_compute_overview"),
    re_path(r"(?P<pk>\d+)/storages/?$", AdminComputeStoragesView.as_view(), name="admin_compute_storages"),
    re_path(
        r"(?P<pk>\d+)/storages/dir_create/?$",
        AdminComputeStorageDirCreateView.as_view(),
        name="admin_compute_storage_dir_create",
    ),
    re_path(
        r"(?P<pk>\d+)/storages/rbd_create/?$",
        AdminComputeStorageRBDCreateView.as_view(),
        name="admin_compute_storage_rbd_create",
    ),
    re_path(
        r"(?P<pk>\d+)/storages/(?P<pool>[\w\d\-]+)/?$", AdminComputeStorageView.as_view(), name="admin_compute_storage"
    ),
    re_path(
        r"(?P<pk>\d+)/storages/(?P<pool>[\w\d\-]+)/delete/?$",
        AdminComputeStorageDeleteView.as_view(),
        name="admin_compute_storage_delete",
    ),
    re_path(
        r"(?P<pk>\d+)/storages/(?P<pool>[\w\d\-]+)/volume/create/?$",
        AdminComputeStorageVolumeCreateView.as_view(),
        name="admin_compute_storage_volume_create",
    ),
    re_path(
        r"(?P<pk>\d+)/storages/(?P<pool>[\w\d\-]+)/volume/(?P<vol>[\w\d\-\.]+)/clone/?$",
        AdminComputeStorageVolumeCloneView.as_view(),
        name="admin_compute_storage_volume_clone",
    ),
    re_path(
        r"(?P<pk>\d+)/storages/(?P<pool>[\w\d\-]+)/volume/(?P<vol>[\w\d\-\.]+)/resize/?$",
        AdminComputeStorageVolumeResizeView.as_view(),
        name="admin_compute_storage_volume_resize",
    ),
    re_path(
        r"(?P<pk>\d+)/storages/(?P<pool>[\w\d\-]+)/volume/(?P<vol>[\w\d\-\.]+)/delete/?$",
        AdminComputeStorageVolumeDeleteView.as_view(),
        name="admin_compute_storage_volume_delete",
    ),
    re_path(r"(?P<pk>\d+)/networks/?$", AdminComputeNetworksView.as_view(), name="admin_compute_networks"),
    re_path(
        r"(?P<pk>\d+)/networks/create/?$", AdminComputeNetworkCreateView.as_view(), name="admin_compute_network_create"
    ),
    re_path(
        r"(?P<pk>\d+)/networks/(?P<pool>[\w\d\-]+)/?$", AdminComputeNetworkView.as_view(), name="admin_compute_network"
    ),
    re_path(
        r"(?P<pk>\d+)/networks/(?P<pool>[\w\d\-]+)/delete/?$",
        AdminComputeNetworkDeleteView.as_view(),
        name="admin_compute_network_delete",
    ),
    re_path(r"(?P<pk>\d+)/secrets/?$", AdminComputeSecretsView.as_view(), name="admin_compute_secrets"),
    re_path(
        r"(?P<pk>\d+)/secrets/create/?$", AdminComputeSecretCreateView.as_view(), name="admin_compute_secret_create"
    ),
    re_path(
        r"(?P<pk>\d+)/secret/(?P<uuid>[\w\d\-]+)/value/?$",
        AdminComputeSecretValueView.as_view(),
        name="admin_compute_secret_value",
    ),
    re_path(
        r"(?P<pk>\d+)/secret/(?P<uuid>[\w\d\-]+)/delete/?$",
        AdminComputeSecretDeleteView.as_view(),
        name="admin_compute_secret_delete",
    ),
    re_path(r"(?P<pk>\d+)/nwfilters/?$", AdminComputeNwfiltersView.as_view(), name="admin_compute_nwfilters"),
    re_path(
        r"(?P<pk>\d+)/nwfilters/create/?$",
        AdminComputeNwfilterCreateView.as_view(),
        name="admin_compute_nwfilter_create",
    ),
    re_path(
        r"(?P<pk>\d+)/nwfilters/(?P<nfilter>[\w\d\-]+)/?$",
        AdminComputeNwfilterView.as_view(),
        name="admin_compute_nwfilter",
    ),
    re_path(
        r"(?P<pk>\d+)/nwfilters/(?P<nfilter>[\w\d\-]+)/delete/?$",
        AdminComputeNwfilterDeleteView.as_view(),
        name="admin_compute_nwfilter_delete",
    ),
]
