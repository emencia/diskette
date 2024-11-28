from django import forms
from django.utils.translation import gettext_lazy as _

from ..models import DumpFile


class DumpFileAdminForm(forms.ModelForm):
    class Meta:
        model = DumpFile
        exclude = []
        fields = [
            "created",
            "processed",
            "deprecated",
            "with_data",
            "with_storage",
            "checksum",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Deprecation field can only be edited from existing and non deprecated object
        if not self.instance.pk or (
            self.instance.pk and self.instance.deprecated
        ):
            self.fields["deprecated"].disabled = True

        # Options are not editable once object has been created
        if self.instance.pk:
            self.fields["with_data"].disabled = True
            self.fields["with_storage"].disabled = True

    def clean(self):
        """
        Add custom global input cleaner validations.
        """
        cleaned_data = super().clean()
        submitted_deprecation = cleaned_data.get("deprecated")

        if self.instance.pk:
            if self.instance.deprecated and not submitted_deprecation:
                self.add_error(
                    "deprecated",
                    forms.ValidationError(
                        _(
                            "Once deprecated a dump can not be available anymore."
                        ),
                        code="invalid",
                    ),
                )
        else:
            if submitted_deprecation:
                self.add_error(
                    "deprecated",
                    forms.ValidationError(
                        _(
                            "You can't create a deprecated dump."
                        ),
                        code="invalid",
                    ),
                )

    def save(self, *args, **kwargs):
        # Deprecate all other available dumps with the same option set when creating a
        # new one
        if not self.instance.pk and not self.cleaned_data["deprecated"]:
            DumpFile.objects.filter(
                deprecated=False,
                with_data=self.instance.with_data,
                with_storage=self.instance.with_storage
            ).update(deprecated=True)

        dump_object = super().save(*args, **kwargs)

        return dump_object
