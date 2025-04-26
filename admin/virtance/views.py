from django.conf import settings
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django_filters.views import FilterView
from django_tables2 import RequestConfig, SingleTableMixin

from admin.mixins import AdminTemplateView, AdminView
from compute.webvirt import WebVirtCompute
from network.models import IPAddress, Network
from virtance.models import Virtance, VirtanceError
from virtance.tasks import action_virtance, create_virtance

from .filters import VirtanceFilter
from .tables import VirtanceErrorTable, VirtanceHTMxTable


class AdminVirtanceIndexView(SingleTableMixin, FilterView, AdminView):
    table_class = VirtanceHTMxTable
    filterset_class = VirtanceFilter
    template_name = "admin/virtance/index.html"

    def get_queryset(self):
        return Virtance.objects.filter(is_deleted=False)

    def get_template_names(self):
        if self.request.htmx:
            return "django_tables2/table_partial.html"
        return self.template_name


class AdminVirtanceDataView(AdminTemplateView):
    template_name = "admin/virtance/virtance.html"

    def get_object(self):
        return get_object_or_404(Virtance, pk=self.kwargs["pk"], is_deleted=False)

    def get_template_names(self):
        if self.request.htmx:
            return "django_tables2/table_partial.html"
        return self.template_name

    def get_context_data(self, **kwargs):
        status = "shutoff"
        virtance = self.get_object()
        context = super().get_context_data(**kwargs)
        virtance_errors = VirtanceError.objects.filter(virtance=virtance)

        if virtance.compute and virtance.event != Virtance.CREATE:
            wvcomp = WebVirtCompute(virtance.compute.token, virtance.compute.hostname)
            res_status = wvcomp.status_virtance(virtance.id)
            if res_status.get("detail"):
                messages.error(self.request, res_status.get("detail"))

            status = res_status.get("status")
            if status == "running":
                virtance.active()
            if status == "shutoff":
                virtance.inactive()

        ipv4public = IPAddress.objects.filter(virtance=virtance, network__type=Network.PUBLIC).first()
        if ipv4public is None:
            messages.error(self.request, "No public IP address assigned to this virtance")

        ipv4private = IPAddress.objects.filter(virtance=virtance, network__type=Network.PRIVATE).first()
        if ipv4private is None:
            messages.error(self.request, "No private IP address assigned to this virtance")

        ipv4compute = IPAddress.objects.filter(virtance=virtance, network__type=Network.COMPUTE).first()
        if ipv4compute is None:
            messages.error(self.request, "No compute IP address assigned to this virtance")

        virtance_errors_table = VirtanceErrorTable(virtance_errors)
        RequestConfig(self.request).configure(virtance_errors_table)

        context["status"] = status
        context["virtance"] = virtance
        context["ipv4public"] = ipv4public
        context["ipv4private"] = ipv4private
        context["ipv4compute"] = ipv4compute
        context["virtance_errors_table"] = virtance_errors_table
        return context


class AdminVirtanceConsoleView(AdminTemplateView):
    template_name = "admin/virtance/console.html"

    def get_object(self):
        return get_object_or_404(Virtance, pk=self.kwargs["pk"])

    def get(self, request, *args, **kwargs):
        virtance = self.get_object()
        response = super(AdminVirtanceConsoleView, self).get(request, *args, **kwargs)
        response.set_cookie("uuid", virtance.uuid, httponly=True, domain=settings.SESSION_COOKIE_DOMAIN)
        return response

    def get_context_data(self, **kwargs):
        virtance = self.get_object()
        context = super().get_context_data(**kwargs)

        wvcomp = WebVirtCompute(virtance.compute.token, virtance.compute.hostname)
        res = wvcomp.get_virtance_vnc(virtance.id)
        vnc_password = res.get("vnc_password")
        console_host = settings.NOVNC_URL
        console_port = settings.NOVNC_PORT

        context["virtance"] = virtance
        context["vnc_password"] = vnc_password
        context["console_host"] = console_host
        context["console_port"] = console_port
        return context


class AdminVirtanceResetEventAction(AdminView):
    def get_object(self):
        return get_object_or_404(Virtance, pk=self.kwargs["pk"])

    def post(self, request, *args, **kwargs):
        virtance = self.get_object()
        virtance.reset_event()
        return redirect(reverse("admin_virtance_data", args=[kwargs.get("pk")]))


class AdminVirtanceRecreateAction(AdminView):
    def get_object(self):
        return get_object_or_404(Virtance, pk=self.kwargs["pk"])

    def post(self, request, *args, **kwargs):
        virtance = self.get_object()
        virtance.event = virtance.CREATE
        virtance.save()
        create_virtance.delay(virtance.id)
        return redirect(reverse("admin_virtance_data", args=[kwargs.get("pk")]))


class AdminVirtancePowerOnAction(AdminView):
    def get_object(self):
        return get_object_or_404(Virtance, pk=self.kwargs["pk"])

    def post(self, request, *args, **kwargs):
        virtance = self.get_object()
        virtance.event = virtance.POWER_ON
        virtance.save()
        action_virtance.delay(virtance.id, "power_on")
        return redirect(reverse("admin_virtance_data", args=[kwargs.get("pk")]))


class AdminVirtancePowerOffAction(AdminView):
    def get_object(self):
        return get_object_or_404(Virtance, pk=self.kwargs["pk"])

    def post(self, request, *args, **kwargs):
        virtance = self.get_object()
        virtance.event = virtance.POWER_OFF
        virtance.save()
        action_virtance.delay(virtance.id, "power_off")
        return redirect(reverse("admin_virtance_data", args=[kwargs.get("pk")]))


class AdminVirtancePowerCyrcleAction(AdminView):
    def get_object(self):
        return get_object_or_404(Virtance, pk=self.kwargs["pk"])

    def post(self, request, *args, **kwargs):
        virtance = self.get_object()
        virtance.event = virtance.POWER_CYCLE
        virtance.save()
        action_virtance.delay(virtance.id, "power_cycle")
        return redirect(reverse("admin_virtance_data", args=[kwargs.get("pk")]))
