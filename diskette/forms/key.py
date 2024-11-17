from django import forms
from django.utils.translation import gettext_lazy as _

from ..models import APIkey


class APIkeyAdminForm(forms.ModelForm):
    class Meta:
        model = APIkey
        exclude = []
        fields = [
            "created",
            "deprecated",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Deprecation field can only be edited for an existing and non deprecated object
        if not self.instance.pk or (
            self.instance.pk and self.instance.deprecated
        ):
            self.fields["deprecated"].disabled = True

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
                            "Once deprecated a key can not be available anymore."
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
                            "You can't create a deprecated key."
                        ),
                        code="invalid",
                    ),
                )

    def save(self, *args, **kwargs):
        # Deprecate all other available keys when creating a new key
        # NOTE: since using 'update()' there won't be cascading updates on involved
        # objects because their model 'save()' won't be called
        if not self.instance.pk and not self.cleaned_data["deprecated"]:
            APIkey.objects.filter(deprecated=False).update(deprecated=True)

        apikey = super().save(*args, **kwargs)

        return apikey
