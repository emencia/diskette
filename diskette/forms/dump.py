from django import forms

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
            "path",
            "checksum",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Deprecation field can only be edited for existing and non deprecated object
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
        deprecated = cleaned_data.get("deprecated")

        if self.instance.pk:
            if self.instance.deprecated and not deprecated:
                self.add_error(
                    "deprecated",
                    forms.ValidationError(
                        _(
                            "You can't change deprecation value."
                        ),
                        code="invalid",
                    ),
                )
        else:
            if deprecated:
                self.add_error(
                    "deprecated",
                    forms.ValidationError(
                        _(
                            "You can't create a deprecated key."
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