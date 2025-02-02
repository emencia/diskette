"""
DumpFile admin interface
"""
from pathlib import Path

from django.contrib import admin
from django.template.defaultfilters import filesizeformat
from django.urls import path, reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from ..core.processes import post_dump_save_process
from ..forms import DumpFileAdminForm
from ..models import DumpFile
from ..views.dump import DumpFileAdminDownloadView
from .actions import make_deprecated
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
        "path_url",
        "humanized_filesize",
        "checksum",
        "logs",
    ]
    list_filter = (
        AvailabilityFilter,
        "created",
    )
    actions = [make_deprecated]

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

    @admin.display(description=_("dump file"))
    def path_url(self, obj):
        """
        Either return the HTML link to download dump (if not deprecated) or just the
        stored value.
        """
        if not obj.path:
            return "-"
        elif obj.deprecated or obj.path.startswith("removed:/"):
            return obj.path

        url = reverse("admin:diskette_admin_dump_download", args=[obj.id])
        link = "<a href=\"{}\" target=\"_blank\" title=\"Download dump file\">{}</a>"
        return mark_safe(link.format(url, obj.path))

    def get_urls(self):
        """
        Set some additional custom admin views
        """
        urls = super().get_urls()

        extra_urls = [
            path(
                "download/dump/<int:pk>.tar.gz",
                self.admin_site.admin_view(
                    DumpFileAdminDownloadView.as_view(),
                ),
                name="diskette_admin_dump_download",
            ),
        ]

        return extra_urls + urls

    def save_model(self, request, obj, form, change):
        """
        .. Todo::
            This is performed under a transaction so if process fail from
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
            This is still efficient but have a flaw with files that cant be deleted from
            the Django instance (like in case of wrong permissions). The selected
            objects from queryset will be deleted but files would still on filesystem
            and there would be no object anymore to know about them.

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

        for filepath in files:
            filepath.unlink(missing_ok=True)
