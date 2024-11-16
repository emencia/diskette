from django.contrib import admin
from django.utils.translation import gettext_lazy as _


class AvailabilityFilter(admin.SimpleListFilter):
    """
    Filter on availability which is in fact the reverse value of ``deprecated`` field.
    """
    title = _("availability")

    # Parameter for the filter that will be used in the URL query.
    parameter_name = "is_available"

    def lookups(self, request, model_admin):
        """
        Build choices from available languages.
        """
        return (
            ("true", _("Is available")),
            ("false", _("Is deprecated")),
        )

    def queryset(self, request, queryset):
        """
        Filter on published or unpublished article depending value is true or false.
        """
        if self.value() == "true":
            return queryset.filter(deprecated=False)

        if self.value() == "false":
            return queryset.filter(deprecated=True)
