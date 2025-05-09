from crispy_forms.bootstrap import InlineCheckboxes
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
from django import forms
from django.conf import settings
from django.urls import reverse_lazy
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin

from admin.mixins import AdminDeleteView, AdminFormView, AdminUpdateView, AdminView
from size.models import DBMS, Size

from .filters import DBMSFilter
from .forms import CustomModelMultipleChoiceField, FormDBMS
from .tables import DBMSHTMxTable


class AdminDBMSIndexView(SingleTableMixin, FilterView, AdminView):
    table_class = DBMSHTMxTable
    filterset_class = DBMSFilter
    template_name = "admin/dbms/index.html"

    def get_queryset(self):
        return DBMS.objects.filter(is_deleted=False)

    def get_template_names(self):
        if self.request.htmx:
            return "django_tables2/table_partial.html"
        return self.template_name


class AdminDBMSCreateView(AdminFormView):
    template_name = "admin/dbms/create.html"
    form_class = FormDBMS
    success_url = reverse_lazy("admin_dbms_index")

    def form_valid(self, form):
        form.save()
        return super(AdminDBMSCreateView, self).form_valid(form)


class AdminDBMSUpdateView(AdminUpdateView):
    template_name = "admin/dbms/update.html"
    template_name_suffix = "_form"
    model = DBMS
    success_url = reverse_lazy("admin_dbms_index")
    fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(AdminDBMSUpdateView, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            "name",
            "slug",
            "description",
            "engine",
            "version",
            InlineCheckboxes("sizes"),
            "is_active",
        )

    def get_form(self, form_class=None):
        form = super(AdminDBMSUpdateView, self).get_form(form_class)
        form.fields["engine"].empty_label = None
        form.fields["sizes"] = CustomModelMultipleChoiceField(
            required=False,
            label="Available for Sizes",
            widget=forms.CheckboxSelectMultiple(),
            queryset=Size.objects.filter(
                memory__gte=settings.DBASS_MIN_VM_MEM_SIZE, type=Size.VIRTANCE, is_deleted=False
            ),
        )
        return form

    def get_context_data(self, **kwargs):
        context = super(AdminDBMSUpdateView, self).get_context_data(**kwargs)
        context["helper"] = self.helper
        return context


class AdminDBMSDeleteView(AdminDeleteView):
    template_name = "admin/dbms/delete.html"
    model = DBMS
    success_url = reverse_lazy("admin_dbms_index")

    def delete(self, request, *args, **kwargs):
        size = self.get_object()
        size.delete()
        return super(self).delete(request, *args, **kwargs)

    def __init__(self, *args, **kwargs):
        super(AdminDBMSDeleteView, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False

    def get_context_data(self, **kwargs):
        context = super(AdminDBMSDeleteView, self).get_context_data(**kwargs)
        context["helper"] = self.helper
        return context
