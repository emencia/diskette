"""
DumpFile admin interface
"""
from django.contrib import admin
from django.template.defaultfilters import filesizeformat
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from ..forms import DumpFileAdminForm
from ..models import DumpFile
from ..core.processes import post_dump_save_process


@admin.register(DumpFile)
class DumpFileAdmin(admin.ModelAdmin):
    form = DumpFileAdminForm
    list_display = (
        "created",
        "processed",
        "status",
        "with_data",
        "with_storage",
        "is_available",
        "humanized_filesize",
    )
    readonly_fields = [
        "created",
        "processed",
        "status",
        "path",
        "humanized_filesize",
        "checksum",
        "logs",
    ]

    def is_available(self, obj):
        """
        Format 'deprecated' value to makes it more intelligible
        """
        return not obj.deprecated
    is_available.short_description = _("available")
    is_available.boolean = True
    is_available.admin_order_field = "-deprecated"

    @admin.display(description=_("archive size"))
    def humanized_filesize(self, obj):
        """
        Format file size to humanized format.
        """
        if not obj.size:
            return "-"

        return filesizeformat(obj.size)
    humanized_filesize.short_description = _("archive size")

    def save_model(self, request, obj, form, change):
        """
        WARNING: This is performed under a transaction so if process fail from
        'post_dump_save_process', dump object won't be saved. We may use Django
        signals instead to execute 'post_dump_save_process'  so it could fail without
        losing object (as we want it for failure history).
        """
        saved = super().save_model(request, obj, form, change)

        post_dump_save_process(obj)
