from crispy_forms.helper import FormHelper
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django_filters.views import FilterView
from django_tables2 import RequestConfig, SingleTableMixin

from admin.mixins import AdminDeleteView, AdminFormView, AdminTemplateView, AdminUpdateView, AdminView
from compute.models import Compute
from compute.webvirt import WebVirtCompute
from network.models import Network
from virtance.models import Virtance

from .filters import ComputeFilter, ComputeOverviewFilter
from .forms import (
    FormAutostartAction,
    FormCompute,
    FormNetworkCreate,
    FormNwfilterCreateAction,
    FormSecretCreateAction,
    FormSecretValueAction,
    FormStartAction,
    FormStorageDirCreate,
    FormStorageRBDCreate,
    FormVolumeCloneAction,
    FormVolumeCreateAction,
    FormVolumeResizeAction,
)
from .tables import (
    ComputeHTMxTable,
    ComputeNetworksTable,
    ComputeNwfilterTable,
    ComputeOverviewHTMxTable,
    ComputeSecretsTable,
    ComputeStoragesTable,
    ComputeStorageVolumesTable,
)


class AdminComputeIndexView(SingleTableMixin, FilterView, AdminView):
    table_class = ComputeHTMxTable
    filterset_class = ComputeFilter
    template_name = "admin/compute/index.html"

    def get_queryset(self):
        return Compute.objects.filter(is_deleted=False)

    def get_template_names(self):
        if self.request.htmx:
            return "django_tables2/table_partial.html"
        return self.template_name


class AdminComputeCreateView(AdminFormView):
    template_name = "admin/compute/create.html"
    form_class = FormCompute
    success_url = reverse_lazy("admin_compute_index")

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class AdminComputeUpdateView(AdminUpdateView):
    template_name = "admin/compute/update.html"
    template_name_suffix = "_form"
    model = Compute
    success_url = reverse_lazy("admin_compute_index")
    fields = ["name", "arch", "description", "hostname", "token", "is_active"]

    def __init__(self, *args, **kwargs):
        super(AdminComputeUpdateView, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False

    def form_valid(self, form):
        if form.has_changed():
            if form.cleaned_data.get("is_active") is True:
                compute = self.get_object()
                network = Network.objects.filter(region=compute.region, is_deleted=False)
                if not network.filter(type=Network.COMPUTE).exists():
                    form.add_error("__all__", "There is no COMPUTE network in the region.")
                    return super().form_invalid(form)
                if not network.filter(type=Network.PRIVATE).exists():
                    form.add_error("__all__", "There is no PRIVATE network in the region.")
                    return super().form_invalid(form)
                if not network.filter(type=Network.PUBLIC).exists():
                    form.add_error("__all__", "There is no PUBLIC network in the region.")
                    return super().form_invalid(form)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(AdminComputeUpdateView, self).get_context_data(**kwargs)
        context["helper"] = self.helper
        return context


class AdminComputeDeleteView(AdminDeleteView):
    template_name = "admin/compute/delete.html"
    model = Compute
    success_url = reverse_lazy("admin_compute_index")

    def delete(self, request, *args, **kwargs):
        compute = self.get_object()
        compute.delete()
        return super(self).delete(request, *args, **kwargs)

    def __init__(self, *args, **kwargs):
        super(AdminComputeDeleteView, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False

    def get_context_data(self, **kwargs):
        context = super(AdminComputeDeleteView, self).get_context_data(**kwargs)
        context["helper"] = self.helper
        return context


class AdminComputeOverviewView(SingleTableMixin, FilterView, AdminView):
    table_class = ComputeOverviewHTMxTable
    filterset_class = ComputeOverviewFilter
    template_name = "admin/compute/overview/index.html"

    def get_queryset(self):
        compute = get_object_or_404(Compute, pk=self.kwargs.get("pk"), is_deleted=False)
        return Virtance.objects.filter(compute=compute, is_deleted=False)

    def get_filterset_kwargs(self, filterset_class):
        kwargs = super().get_filterset_kwargs(filterset_class)
        kwargs["compute_id"] = self.kwargs.get("pk")
        return kwargs

    def get_template_names(self):
        if self.request.htmx:
            return "django_tables2/table_partial.html"
        return self.template_name

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        compute = get_object_or_404(Compute, pk=self.kwargs.get("pk"), is_deleted=False)
        wvcomp = WebVirtCompute(compute.token, compute.hostname)
        res = wvcomp.get_host_overview()
        messages.error(self.request, res.get("detail"))
        context["compute"] = compute
        context["host_overview"] = res
        return context


class AdminComputeStoragesView(AdminTemplateView):
    template_name = "admin/compute/storages/index.html"

    def get_template_names(self):
        if self.request.htmx:
            return "django_tables2/table_partial.html"
        return self.template_name

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        compute = get_object_or_404(Compute, pk=kwargs.get("pk"), is_deleted=False)
        wvcomp = WebVirtCompute(compute.token, compute.hostname)
        res = wvcomp.get_storages()
        messages.error(self.request, res.get("detail"))

        stotages_table_data = []
        for storage in res.get("storages"):
            stotages_table_data.append(
                {
                    "name": storage.get("name"),
                    "type": storage.get("type"),
                    "size": storage.get("size"),
                    "active": storage.get("active"),
                    "state": storage.get("state"),
                    "volumes": storage.get("volumes"),
                }
            )
        storages_table = ComputeStoragesTable(stotages_table_data)
        RequestConfig(self.request).configure(storages_table)

        context["compute"] = compute
        context["storages_table"] = storages_table
        return context


class AdminComputeStorageDirCreateView(AdminFormView):
    template_name = "admin/compute/storages/create_dir_storage.html"
    form_class = FormStorageDirCreate

    def form_valid(self, form):
        compute = get_object_or_404(Compute, pk=self.kwargs.get("pk"), is_deleted=False)
        wvcomp = WebVirtCompute(compute.token, compute.hostname)
        res = wvcomp.create_storage_dir(form.cleaned_data.get("name"), form.cleaned_data.get("target"))
        if res.get("detail") is None:
            return super().form_valid(form)
        form.add_error("__all__", res.get("detail"))
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        compute = get_object_or_404(Compute, pk=self.kwargs.get("pk"), is_deleted=False)
        context["compute"] = compute
        return context

    def get_success_url(self):
        return reverse("admin_compute_storages", args=[self.kwargs.get("pk")])


class AdminComputeStorageRBDCreateView(AdminFormView):
    template_name = "admin/compute/storages/create_rbd_storage.html"
    form_class = FormStorageRBDCreate

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        compute = get_object_or_404(Compute, pk=self.kwargs.get("pk"), is_deleted=False)
        wvcomp = WebVirtCompute(compute.token, compute.hostname)
        res = wvcomp.get_secrets()
        form.fields["secret"].choices = [(secret.get("uuid"), secret.get("uuid")) for secret in res.get("secrets")]
        return form

    def form_valid(self, form):
        compute = get_object_or_404(Compute, pk=self.kwargs.get("pk"), is_deleted=False)
        wvcomp = WebVirtCompute(compute.token, compute.hostname)
        res = wvcomp.create_storage_rbd(
            form.cleaned_data.get("name"),
            form.cleaned_data.get("pool"),
            form.cleaned_data.get("user"),
            form.cleaned_data.get("secret"),
            form.cleaned_data.get("host"),
            form.cleaned_data.get("host2"),
            form.cleaned_data.get("host3"),
        )
        if res.get("detail") is None:
            return super().form_valid(form)
        form.add_error("__all__", res.get("detail"))
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        compute = get_object_or_404(Compute, pk=self.kwargs.get("pk"), is_deleted=False)
        context["compute"] = compute
        return context

    def get_success_url(self):
        return reverse("admin_compute_storages", args=[self.kwargs.get("pk")])


class AdminComputeStorageView(AdminTemplateView):
    template_name = "admin/compute/storages/storage.html"

    def get_template_names(self):
        if self.request.htmx:
            return "django_tables2/table_partial.html"
        return self.template_name

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        compute = get_object_or_404(Compute, pk=kwargs.get("pk"), is_deleted=False)
        wvcomp = WebVirtCompute(compute.token, compute.hostname)
        res = wvcomp.get_storage(kwargs.get("pool"))
        storage_pool = res.get("storage")
        messages.error(self.request, res.get("detail"))

        volumes_table_data = []
        for volume in storage_pool.get("volumes"):
            volumes_table_data.append(
                {
                    "name": volume.get("name"),
                    "size": volume.get("size"),
                    "type": volume.get("type"),
                }
            )
        volumes_table = ComputeStorageVolumesTable(volumes_table_data)
        RequestConfig(self.request).configure(volumes_table)

        context["form_start"] = FormStartAction()
        context["form_autostart"] = FormAutostartAction()
        context["compute"] = compute
        context["storage_pool"] = storage_pool
        context["volumes_table"] = volumes_table
        return context

    def post(self, request, *args, **kwargs):
        form_start = FormStartAction(request.POST)
        form_autostart = FormAutostartAction(request.POST)
        context = self.get_context_data(*args, **kwargs)

        if form_start.is_valid():
            compute = get_object_or_404(Compute, pk=kwargs.get("pk"), is_deleted=False)
            wvcomp = WebVirtCompute(compute.token, compute.hostname)
            res = wvcomp.set_storage_action(kwargs.get("pool"), form_start.cleaned_data.get("action"))
            if res.get("detail") is None:
                return redirect(self.request.get_full_path())
            messages.error(self.request, res.get("detail"))
            context["form_start"] = form_start

        if form_autostart.is_valid():
            compute = get_object_or_404(Compute, pk=kwargs.get("pk"), is_deleted=False)
            wvcomp = WebVirtCompute(compute.token, compute.hostname)
            res = wvcomp.set_storage_action(kwargs.get("pool"), form_autostart.cleaned_data.get("action"))
            if res.get("detail") is None:
                return redirect(self.request.get_full_path())
            messages.error(self.request, res.get("detail"))
            context["form_autostart"] = form_autostart

        return self.render_to_response(context)


class AdminComputeStorageDeleteView(AdminView):
    def get(self, request, *args, **kwargs):
        succes_url = redirect(request.get_full_path())
        compute = get_object_or_404(Compute, pk=kwargs.get("pk"), is_deleted=False)
        wvcomp = WebVirtCompute(compute.token, compute.hostname)
        res = wvcomp.delete_storage(kwargs.get("pool"))
        if res.get("detail") is None:
            messages.success(request, "Storage successfuly deleted.")
            succes_url = redirect(reverse("admin_compute_storages", args=kwargs.get("pk")))
        else:
            messages.error(request, res.get("detail"))
        return succes_url


class AdminComputeStorageVolumeCreateView(AdminFormView):
    template_name = "admin/compute/storages/volumes/create.html"
    form_class = FormVolumeCreateAction

    def form_valid(self, form):
        compute = get_object_or_404(Compute, pk=self.kwargs.get("pk"), is_deleted=False)
        wvcomp = WebVirtCompute(compute.token, compute.hostname)
        res = wvcomp.create_storage_volume(
            self.kwargs.get("pool"),
            form.cleaned_data.get("name"),
            form.cleaned_data.get("size"),
            form.cleaned_data.get("format"),
        )
        if res.get("detail") is not None:
            form.add_error("__all__", res.get("detail"))
            return super().form_invalid(form)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        compute = get_object_or_404(Compute, pk=self.kwargs.get("pk"), is_deleted=False)
        context["compute"] = compute
        context["pool"] = self.kwargs.get("pool")
        return context

    def get_success_url(self):
        return reverse("admin_compute_storage", args=[self.kwargs.get("pk"), self.kwargs.get("pool")])


class AdminComputeStorageVolumeCloneView(AdminFormView):
    template_name = "admin/compute/storages/volumes/clone.html"
    form_class = FormVolumeCloneAction

    def form_valid(self, form):
        compute = get_object_or_404(Compute, pk=self.kwargs.get("pk"), is_deleted=False)
        wvcomp = WebVirtCompute(compute.token, compute.hostname)
        res = wvcomp.action_storage_volume(
            self.kwargs.get("pool"), self.kwargs.get("vol"), "clone", form.cleaned_data.get("name")
        )
        if res.get("detail") is not None:
            form.add_error("__all__", res.get("detail"))
            return super().form_invalid(form)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        compute = get_object_or_404(Compute, pk=self.kwargs.get("pk"), is_deleted=False)
        context["compute"] = compute
        context["pool"] = self.kwargs.get("pool")
        context["vol"] = self.kwargs.get("vol")
        return context

    def get_success_url(self):
        return reverse("admin_compute_storage", args=[self.kwargs.get("pk"), self.kwargs.get("pool")])


class AdminComputeStorageVolumeResizeView(AdminFormView):
    template_name = "admin/compute/storages/volumes/resize.html"
    form_class = FormVolumeResizeAction

    def form_valid(self, form):
        compute = get_object_or_404(Compute, pk=self.kwargs.get("pk"), is_deleted=False)
        wvcomp = WebVirtCompute(compute.token, compute.hostname)
        res = wvcomp.action_storage_volume(
            self.kwargs.get("pool"), self.kwargs.get("vol"), "resize", form.cleaned_data.get("size") * (1024**3)
        )
        if res.get("detail") is not None:
            form.add_error("__all__", res.get("detail"))
            return super().form_invalid(form)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        compute = get_object_or_404(Compute, pk=self.kwargs.get("pk"), is_deleted=False)
        context["compute"] = compute
        context["pool"] = self.kwargs.get("pool")
        context["vol"] = self.kwargs.get("vol")
        return context

    def get_success_url(self):
        return reverse("admin_compute_storage", args=[self.kwargs.get("pk"), self.kwargs.get("pool")])


class AdminComputeStorageVolumeDeleteView(AdminView):
    def get(self, request, *args, **kwargs):
        compute = get_object_or_404(Compute, pk=kwargs.get("pk"), is_deleted=False)
        wvcomp = WebVirtCompute(compute.token, compute.hostname)
        res = wvcomp.delete_storage_volume(kwargs.get("pool"), kwargs.get("vol"))
        if res.get("detail") is None:
            messages.success(request, "Volume successfuly deleted.")
        else:
            messages.error(request, res.get("detail"))
        return redirect(reverse("admin_compute_storage", args=[kwargs.get("pk"), kwargs.get("pool")]))


class AdminComputeNetworkCreateView(AdminFormView):
    template_name = "admin/compute/networks/create.html"
    form_class = FormNetworkCreate

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        compute = get_object_or_404(Compute, pk=self.kwargs.get("pk"), is_deleted=False)
        wvcomp = WebVirtCompute(compute.token, compute.hostname)
        res = wvcomp.get_interfaces()
        form.fields["bridge_name"].choices = [
            (iface.get("name"), iface.get("name")) for iface in res.get("interfaces") if iface.get("type") == "bridge"
        ]
        return form

    def form_valid(self, form):
        compute = get_object_or_404(Compute, pk=self.kwargs.get("pk"), is_deleted=False)
        wvcomp = WebVirtCompute(compute.token, compute.hostname)
        res = wvcomp.create_network(
            form.cleaned_data.get("name"), form.cleaned_data.get("bridge_name"), form.cleaned_data.get("openvswitch")
        )
        if res.get("detail") is None:
            return super().form_valid(form)
        form.add_error("__all__", res.get("detail"))
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        compute = get_object_or_404(Compute, pk=self.kwargs.get("pk"), is_deleted=False)
        context["compute"] = compute
        return context

    def get_success_url(self):
        return reverse("admin_compute_networks", args=[self.kwargs.get("pk")])


class AdminComputeNetworksView(AdminTemplateView):
    template_name = "admin/compute/networks/index.html"

    def get_template_names(self):
        if self.request.htmx:
            return "django_tables2/table_partial.html"
        return self.template_name

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        compute = get_object_or_404(Compute, pk=kwargs.get("pk"), is_deleted=False)
        wvcomp = WebVirtCompute(compute.token, compute.hostname)
        res = wvcomp.get_networks()
        messages.error(self.request, res.get("detail"))

        networks_table_data = []
        for network in res.get("networks"):
            networks_table_data.append(
                {
                    "name": network.get("name"),
                    "device": network.get("device"),
                    "active": network.get("active"),
                    "forward": network.get("forward"),
                }
            )
        networks_table = ComputeNetworksTable(networks_table_data)
        RequestConfig(self.request).configure(networks_table)

        context["compute"] = compute
        context["networks_table"] = networks_table
        return context


class AdminComputeNetworkView(AdminTemplateView):
    template_name = "admin/compute/networks/network.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        compute = get_object_or_404(Compute, pk=kwargs.get("pk"), is_deleted=False)
        wvcomp = WebVirtCompute(compute.token, compute.hostname)
        res = wvcomp.get_network(kwargs.get("pool"))
        messages.error(self.request, res.get("detail"))
        context["compute"] = compute
        context["form_start"] = FormStartAction()
        context["form_autostart"] = FormAutostartAction()
        context["network_pool"] = res.get("network")
        return context

    def post(self, request, *args, **kwargs):
        form_start = FormStartAction(request.POST)
        form_autostart = FormAutostartAction(request.POST)
        context = self.get_context_data(*args, **kwargs)

        if form_start.is_valid():
            compute = get_object_or_404(Compute, pk=kwargs.get("pk"), is_deleted=False)
            wvcomp = WebVirtCompute(compute.token, compute.hostname)
            res = wvcomp.set_network_action(kwargs.get("pool"), form_start.cleaned_data.get("action"))
            if res.get("detail") is None:
                return redirect(self.request.get_full_path())
            messages.error(self.request, res.get("detail"))
            context["form_start"] = form_start

        if form_autostart.is_valid():
            compute = get_object_or_404(Compute, pk=kwargs.get("pk"), is_deleted=False)
            wvcomp = WebVirtCompute(compute.token, compute.hostname)
            res = wvcomp.set_network_action(kwargs.get("pool"), form_autostart.cleaned_data.get("action"))
            if res.get("detail") is None:
                return redirect(self.request.get_full_path())
            messages.error(self.request, res.get("detail"))
            context["form_autostart"] = form_autostart

        return self.render_to_response(context)


class AdminComputeNetworkDeleteView(AdminView):
    def get(self, request, *args, **kwargs):
        succes_url = redirect(request.get_full_path())
        compute = get_object_or_404(Compute, pk=kwargs.get("pk"), is_deleted=False)
        wvcomp = WebVirtCompute(compute.token, compute.hostname)
        res = wvcomp.delete_network(kwargs.get("pool"))
        if res.get("detail") is None:
            messages.success(request, "Network successfuly deleted.")
            succes_url = redirect(reverse("admin_compute_networks", args=kwargs.get("pk")))
        else:
            messages.error(request, res.get("detail"))
        return succes_url


class AdminComputeSecretsView(AdminTemplateView):
    template_name = "admin/compute/secrets/index.html"

    def get_template_names(self):
        if self.request.htmx:
            return "django_tables2/table_partial.html"
        return self.template_name

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        compute = get_object_or_404(Compute, pk=kwargs.get("pk"), is_deleted=False)
        wvcomp = WebVirtCompute(compute.token, compute.hostname)
        res = wvcomp.get_secrets()
        messages.error(self.request, res.get("detail"))

        secrets_table_data = []
        for secret in res.get("secrets"):
            secrets_table_data.append(
                {
                    "uuid": secret.get("uuid"),
                    "type": secret.get("usageType"),
                    "usage": secret.get("usage"),
                    "value": secret.get("value"),
                }
            )
        secrets_table = ComputeSecretsTable(secrets_table_data)
        RequestConfig(self.request).configure(secrets_table)

        context["compute"] = compute
        context["secrets_table"] = secrets_table
        return context


class AdminComputeSecretCreateView(AdminFormView):
    template_name = "admin/compute/secrets/create.html"
    form_class = FormSecretCreateAction

    def form_valid(self, form):
        compute = get_object_or_404(Compute, pk=self.kwargs.get("pk"), is_deleted=False)
        wvcomp = WebVirtCompute(compute.token, compute.hostname)
        res = wvcomp.create_secret(
            form.cleaned_data.get("ephemeral"),
            form.cleaned_data.get("private"),
            form.cleaned_data.get("type"),
            form.cleaned_data.get("data"),
        )
        if res.get("detail") is not None:
            form.add_error("__all__", res.get("detail"))
            return super().form_invalid(form)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        compute = get_object_or_404(Compute, pk=self.kwargs.get("pk"), is_deleted=False)
        context["compute"] = compute
        return context

    def get_success_url(self):
        return reverse("admin_compute_secrets", args=self.kwargs.get("pk"))


class AdminComputeSecretValueView(AdminFormView):
    template_name = "admin/compute/secrets/value.html"
    form_class = FormSecretValueAction

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        compute = get_object_or_404(Compute, pk=self.kwargs.get("pk"), is_deleted=False)
        wvcomp = WebVirtCompute(compute.token, compute.hostname)
        res = wvcomp.get_secret(self.kwargs.get("uuid"))
        secret = res.get("secret")
        form.fields["value"].initial = secret.get("value")
        return form

    def form_valid(self, form):
        compute = get_object_or_404(Compute, pk=self.kwargs.get("pk"), is_deleted=False)
        wvcomp = WebVirtCompute(compute.token, compute.hostname)
        res = wvcomp.update_secret_value(self.kwargs.get("uuid"), form.cleaned_data.get("value"))
        if res.get("detail") is not None:
            form.add_error("__all__", res.get("detail"))
            return super().form_invalid(form)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        compute = get_object_or_404(Compute, pk=self.kwargs.get("pk"), is_deleted=False)
        context["uuid"] = self.kwargs.get("uuid")
        context["compute"] = compute
        return context

    def get_success_url(self):
        return reverse("admin_compute_secrets", args=self.kwargs.get("pk"))


class AdminComputeSecretDeleteView(AdminView):
    def get(self, request, *args, **kwargs):
        compute = get_object_or_404(Compute, pk=kwargs.get("pk"), is_deleted=False)
        wvcomp = WebVirtCompute(compute.token, compute.hostname)
        res = wvcomp.delete_secret(kwargs.get("uuid"))
        if res.get("detail") is None:
            messages.success(request, "Secret successfuly deleted.")
        else:
            messages.error(request, res.get("detail"))
        return redirect(reverse("admin_compute_secrets", args=kwargs.get("pk")))


class AdminComputeNwfiltersView(AdminTemplateView):
    template_name = "admin/compute/nwfilters/index.html"

    def get_template_names(self):
        if self.request.htmx:
            return "django_tables2/table_partial.html"
        return self.template_name

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        compute = get_object_or_404(Compute, pk=kwargs.get("pk"), is_deleted=False)
        wvcomp = WebVirtCompute(compute.token, compute.hostname)
        res = wvcomp.get_nwfilters()
        messages.error(self.request, res.get("detail"))

        nwfilters_table_data = []
        for nwfilter in res.get("nwfilters"):
            nwfilters_table_data.append(
                {
                    "name": nwfilter.get("name"),
                }
            )
        nwfilters_table = ComputeNwfilterTable(nwfilters_table_data)
        RequestConfig(self.request).configure(nwfilters_table)

        context["compute"] = compute
        context["nwfilters_table"] = nwfilters_table
        return context


class AdminComputeNwfilterCreateView(AdminFormView):
    template_name = "admin/compute/nwfilters/create.html"
    form_class = FormNwfilterCreateAction

    def form_valid(self, form):
        compute = get_object_or_404(Compute, pk=self.kwargs.get("pk"), is_deleted=False)
        wvcomp = WebVirtCompute(compute.token, compute.hostname)
        res = wvcomp.create_nwfilter(form.cleaned_data.get("xml"))
        if res.get("detail") is not None:
            form.add_error("__all__", res.get("detail"))
            return super().form_invalid(form)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        compute = get_object_or_404(Compute, pk=self.kwargs.get("pk"), is_deleted=False)
        context["compute"] = compute
        return context

    def get_success_url(self):
        return reverse("admin_compute_nwfilters", args=self.kwargs.get("pk"))


class AdminComputeNwfilterView(AdminTemplateView):
    template_name = "admin/compute/nwfilters/nwfilter.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        compute = get_object_or_404(Compute, pk=self.kwargs.get("pk"), is_deleted=False)
        wvcomp = WebVirtCompute(compute.token, compute.hostname)
        res = wvcomp.view_nwfilter(kwargs.get("nfilter"))
        messages.error(self.request, res.get("detail"))
        context["compute"] = compute
        context["nwfilter"] = res.get("nwfilter")
        return context


class AdminComputeNwfilterDeleteView(AdminView):
    def get(self, request, *args, **kwargs):
        compute = get_object_or_404(Compute, pk=kwargs.get("pk"), is_deleted=False)
        wvcomp = WebVirtCompute(compute.token, compute.hostname)
        res = wvcomp.delete_nwfilter(kwargs.get("nfilter"))
        if res.get("detail") is None:
            messages.success(request, "NwFilter successfuly deleted.")
        else:
            messages.error(request, res.get("detail"))
        return redirect(reverse("admin_compute_nwfilters", args=[kwargs.get("pk")]))
