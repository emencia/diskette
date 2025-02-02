from django.http import HttpResponse
from django.views import View
from django.views.generic.detail import SingleObjectMixin

from django_sendfile import sendfile

from ..models import DumpFile


class DumpFileAdminDownloadView(SingleObjectMixin, View):
    """
    View to download a dump from admin.

    .. Todo::
        This view is only for admin browsing. Another view will be developed for the
        futur client since it will not be subject to authentication and rather use the
        APIKey.
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

        return sendfile(
            request,
            dump.get_absolute_path(),
            encoding="tar",
            attachment=True,
            mimetype="application/x-gzip"
        )


class DumpLogAdminView(SingleObjectMixin, View):
    """
    View to display dump logs (in plain text) from admin..
    """
    model = DumpFile
    http_method_names = ["get", "head", "options", "trace"]

    def get(self, request, *args, **kwargs):
        """
        Send file to download.
        """
        dump = self.get_object()

        return HttpResponse(dump.logs, content_type="text/plain; charset=utf8")
