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
            dump (Path): Path to the dump file to load.

        Keyword Arguments:
            app (string): Application name. If given, only data from this application
                will be loaded, the other ones will be ignored.
            excludes (list): A list of application or FQM labels to ignore from
                loaded data.
            ignorenonexistent (boolean): If enabled, fields and models that does not
                exists in current models will be ignored instead of raising an error.

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
            dump (Path): Path to the dump file to load.

        Keyword Arguments:
            app (string): Application name. If given, only data from this application
                will be loaded, the other ones will be ignored.
            excludes (list): A list of application or FQM labels to ignore from
                loaded data.
            ignorenonexistent (boolean): If enabled, fields and models that does not
                exists in current models will be ignored instead of raising an error.

        Returns:
            string: Output from command.
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
        logger (object): Instance of a logger object to use. Logger object must
            implement common logging message methods (like error, info, etc..). See
            ``diskette.utils.loggers`` for available loggers. If not given, a dummy
            logger will be used that ignores any messages and won't output anything.
    """
    def __init__(self, executable=None, logger=None):
        self.executable = executable + " " if executable else ""
        self.logger = logger or NoOperationLogger()
