"""
DumpFile admin interface
"""
from pathlib import Path

from django.contrib import admin
from django.template.defaultfilters import filesizeformat
from django.utils.translation import gettext_lazy as _

from ..forms import DumpFileAdminForm
from ..models import DumpFile
from ..core.processes import post_dump_save_process
from .filters import AvailabilityFilter


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
    list_filter = (
        AvailabilityFilter,
        "created",
    )

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
        signals instead (or something else) to detach 'post_dump_save_process'
        execution so it could fail without losing object (as we want it for failure
        history).
        """
        super().save_model(request, obj, form, change)

        post_dump_save_process(obj)

    def delete_queryset(self, request, queryset):
        """
        Customized method for the 'delete selected objects' admin action to correctly
        remove dump files.

        Instead of the legacy admin action this one performs an additional queryset
        to get the dump file paths. Then performs the queryset deletion and finally
        remove path files.

        .. Warning::
            This is still efficient but have a flaw with files that can be delete from
            the Django instance (like because of wrong permissions). Selected objects
            from queryset will be delete but files would still on filesystem and there
            would be no object anymore to know about them.

        .. Todo::
            We could filter out path files that seems impossible to delete from
            permissions. It would need a more advanced algorithm checking about chmod
            and current thread user.
        """
        files = [
            Path(item)
            for item in queryset.exclude(
                path__startswith="removed:/"
            ).values_list("path", flat=True)
        ]

        queryset.delete()

        for path in files:
            path.unlink(missing_ok=True)
