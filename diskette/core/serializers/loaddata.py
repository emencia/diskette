from io import StringIO

from django.core import management
from django.template.defaultfilters import filesizeformat

from ...utils.loggers import NoOperationLogger


class LoaddataSerializerAbstract:
    """
    Data loader serializer is in charge to load data fixtures in database with Django
    loaddata command.

    For now, this is JSON format only, 'format' option may be implemented later.
    """
    COMMAND_NAME = "loaddata"
    COMMAND_TEMPLATE = "{executable}loaddata {options}"

    def command(self, dump, app=None, excludes=None, ignorenonexistent=False):
        """
        Build command line to use ``loaddata``.

        Arguments:
            dump (Path):

        Keyword Arguments:
            app (string):
            excludes (list):
            ignorenonexistent (boolean):

        Returns:
            string: Command line to run a loaddata job.
        """
        options = [str(dump)]

        if app:
            options.append("--app={}".format(app))

        if ignorenonexistent:
            options.append("--ignorenonexistent")

        if excludes:
            options.append(" ".join([
                "--exclude {}".format(item)
                for item in excludes
            ]))

        return self.COMMAND_TEMPLATE.format(
            executable=self.executable,
            dump=dump,
            options=" ".join(options),
        )

    def call(self, dump, app=None, excludes=None, ignorenonexistent=False):
        """
        Programmatically use the Django ``loaddata`` command to dump application.

        Arguments:
            dump (Path):

        Keyword Arguments:
            app (string):
            excludes (list):
            ignorenonexistent (boolean):

        Returns:
            string: A JSON payload of call results. On default, this is the JSON
            output from dumpdata. However if destination has been given, dumpdata has
            written output to a file and so the returned JSON will just be a
            dictionnary with an item ``destination`` with written file path.
        """
        options = {
            "app": app,
            "ignorenonexistent": ignorenonexistent,
            "exclude": excludes or [],
        }

        self.logger.info("Loading data from dump '{path}' ({size})".format(
            path=dump.name,
            size=filesizeformat(dump.stat().st_size)))

        out = StringIO()
        management.call_command(self.COMMAND_NAME, dump, stdout=out, **options)

        content = out.getvalue()
        out.close()

        self.logger.debug(content.strip())

        return content.strip()


class LoaddataSerializer(LoaddataSerializerAbstract):
    """
    Concrete basic implementation for ``LoaddataSerializerAbstract``.

    Keyword Arguments:
        executable (string): A path to prefix commands, commonly the path to
            django-admin (or equivalent). This path will suffixed with a single space
            to ensure separation with command arguments.
        logger (object):
    """
    def __init__(self, executable=None, logger=None):
        self.executable = executable + " " if executable else ""
        self.logger = logger or NoOperationLogger()
