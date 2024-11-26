from django.contrib import admin
from django.utils.translation import gettext_lazy as _


@admin.action(description=_("Deprecate selected objects"))
def make_deprecated(modeladmin, request, queryset):
    """
    Admin action to deprecate selected objects from queryset.
    """
    queryset.update(deprecated=True)
