from django.views import View
from django.views.generic.detail import SingleObjectMixin

from django_sendfile import sendfile

from ..models import DumpFile


class DumpFileAdminDownloadView(SingleObjectMixin, View):
    """
    View to download a dump from admin.

    This view is intended to be included in admin site only where it naturally benefits
    of its authentication so only staff user can download the dump.

    .. Todo::
        This view is only for admin browsing. Another view will be need for the client
        since it will be not subject to authentication rather use the APIKey.
    """
    model = DumpFile
    http_method_names = ["get", "head", "options", "trace"]

    def get_queryset(self):
        """
        Exclude empty path, deprecated and purged dump.
        """
        return super().get_queryset().filter(deprecated=False).exclude(path="").exclude(
            path__startswith="removed:/"
        )

    def get(self, request, *args, **kwargs):
        """
        Send file to download.
        """
        dump = self.get_object()
        return sendfile(request, dump.get_absolute_path(), mimetype="application/gzip")
