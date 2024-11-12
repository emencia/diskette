"""
APIkey admin interface
"""
from django.contrib import admin
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from ..forms import APIkeyAdminForm
from ..models import APIkey


@admin.register(APIkey)
class APIkeyAdmin(admin.ModelAdmin):
    form = APIkeyAdminForm
    list_display = (
        "created",
        "is_available",
    )
    readonly_fields = [
        "created",
        "api_key",
    ]

    @admin.display(description=_("public key"))
    def api_key(self, instance):
        """
        Format 'api_key' value to display it if not empty else display a notice
        """
        if instance.id:
            return mark_safe("<code>{}</code>".format(instance.key))

        return mark_safe("<span>Will be automatically created.</span>")

    def is_available(self, obj):
        """
        Format 'deprecated' value to makes it more intelligible
        """
        return not obj.deprecated
    is_available.short_description = _("available")
    is_available.boolean = True
    is_available.admin_order_field = "-deprecated"
