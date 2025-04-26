from crispy_forms.bootstrap import InlineCheckboxes
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
from django import forms

from image.models import Image
from region.models import Region


class CustomModelMultipleChoiceField(forms.ModelMultipleChoiceField):
    type_input = "checkbox"

    def label_from_instance(self, item):
        return f"{item.name}"


class FormTemplate(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(FormTemplate, self).__init__(*args, **kwargs)
        self.fields["type"] = forms.ChoiceField(
            widget=forms.Select, choices=Image.TYPE_CHOICES, initial=Image.DISTRIBUTION
        )
        self.fields["distribution"] = forms.ChoiceField(
            widget=forms.Select, choices=Image.DISTRO_CHOICES, initial=Image.UBUNTU
        )
        self.fields["regions"] = CustomModelMultipleChoiceField(
            queryset=Region.objects.filter(is_deleted=False), widget=forms.CheckboxSelectMultiple(), required=False
        )
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            "name",
            "slug",
            "type",
            "description",
            "md5sum",
            "distribution",
            "arch",
            "file_name",
            InlineCheckboxes("regions"),
        )

    class Meta:
        model = Image
        fields = "__all__"
