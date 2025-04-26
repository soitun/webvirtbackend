from ipaddress import ip_network

from crispy_forms.helper import FormHelper
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin

from admin.mixins import AdminDeleteView, AdminFormView, AdminUpdateView, AdminView
from network.models import IPAddress, Network

from .filters import NetworkFilter, NetworkListFilter
from .forms import FormNetwork
from .tables import NetworkHTMxTable, NetworkListHTMxTable


class AdminNetworkIndexView(SingleTableMixin, FilterView, AdminView):
    table_class = NetworkHTMxTable
    filterset_class = NetworkFilter
    template_name = "admin/network/index.html"

    def get_queryset(self):
        return Network.objects.filter(is_deleted=False)

    def get_template_names(self):
        if self.request.htmx:
            return "django_tables2/table_partial.html"
        return self.template_name


class AdminNetworkCreateView(AdminFormView):
    template_name = "admin/network/create.html"
    form_class = FormNetwork
    success_url = reverse_lazy("admin_network_index")

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class AdminNetworkUpdateView(AdminUpdateView):
    template_name = "admin/network/update.html"
    template_name_suffix = "_form"
    model = Network
    success_url = reverse_lazy("admin_network_index")
    fields = ["cidr", "netmask", "dns1", "dns2", "is_active"]

    def __init__(self, *args, **kwargs):
        super(AdminNetworkUpdateView, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False

    def dispatch(self, request, *args, **kwargs):
        if IPAddress.objects.filter(network_id=kwargs.get("pk")).exists():
            messages.error(self.request, "Network has assigned IP addresses and cannot be updated")
            return redirect(reverse_lazy("admin_network_index"))
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        cidr = form.cleaned_data.get("cidr")
        netmask = form.cleaned_data.get("netmask")
        subnet = ip_network(f"{cidr}/{netmask}")
        self.object.gateway = str(subnet[1])
        self.object.save()
        form.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(AdminNetworkUpdateView, self).get_context_data(**kwargs)
        context["helper"] = self.helper
        return context


class AdminNetworkDeleteView(AdminDeleteView):
    template_name = "admin/network/delete.html"
    model = Network
    success_url = reverse_lazy("admin_network_index")

    def delete(self, request, *args, **kwargs):
        region = self.get_object()
        region.delete()
        return super(self).delete(request, *args, **kwargs)

    def __init__(self, *args, **kwargs):
        super(AdminNetworkDeleteView, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False

    def dispatch(self, request, *args, **kwargs):
        if IPAddress.objects.filter(network_id=kwargs.get("pk")).exists():
            messages.error(self.request, "Network has assigned IP addresses and cannot be deleted")
            return redirect(reverse_lazy("admin_network_index"))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(AdminNetworkDeleteView, self).get_context_data(**kwargs)
        context["helper"] = self.helper
        return context


class AdminNetworkListView(SingleTableMixin, FilterView, AdminView):
    table_class = NetworkListHTMxTable
    filterset_class = NetworkListFilter
    template_name = "admin/network/list.html"

    def get_queryset(self):
        network = Network.objects.filter(pk=self.kwargs.get("pk")).first()
        return IPAddress.objects.filter(network=network)

    def get_filterset_kwargs(self, filterset_class):
        kwargs = super().get_filterset_kwargs(filterset_class)
        kwargs["network_id"] = self.kwargs.get("pk")
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(AdminNetworkListView, self).get_context_data(**kwargs)
        context["network"] = Network.objects.filter(pk=self.kwargs.get("pk")).first()
        return context

    def get_template_names(self):
        if self.request.htmx:
            return "django_tables2/table_partial.html"
        return self.template_name
