import json
from pathlib import Path
from io import StringIO

from django.core import management
from django.template.defaultfilters import filesizeformat

from ..utils.loggers import NoOperationLogger


class DumpDataSerializerAbstract:
    """
    Dump data serializer is in charge to serialize applications with Django dumpdata
    command.

    For now, this is JSON format only, 'format' option may be implemented later.
    """
    COMMAND_NAME = "dumpdata"
    COMMAND_TEMPLATE = "{executable}dumpdata {options}"

    def merge_excludes(self, source, extra):
        """
        Safely merge source and extra list without duplicate items.
        """
        source = source or []
        extra = extra or []

        merged = [v for v in source]
        merged.extend(v for v in extra if v not in source)

        return merged

    def serialize_command(self, application, destination=None, indent=None,
                          extra_excludes=None):
        """
        Build command line to use ``dumpdata``.

        TODO: Rename to "command"

        Arguments:
            application (ApplicationModel):

        Keyword Arguments:
            destination (Pathlib):
            indent (integer):
            extra_excludes (list):

        Returns:
            string: Command line to run a dumpdata job.
        """
        options = []

        if application.is_drain is True:
            options.append("--all")

        if indent:
            options.append("--indent={}".format(indent))

        if application.models:
            options.append(" ".join(application.models))

        if application.natural_foreign:
            options.append("--natural-foreign")

        if application.natural_primary:
            options.append("--natural-primary")

        complete_excludes = self.merge_excludes(application.excludes, extra_excludes)
        if complete_excludes:
            options.append(" ".join([
                "--exclude {}".format(item)
                for item in complete_excludes
            ]))

        if destination:
            options.append("--output={}".format(
                str(Path(destination) / application.filename)
            ))

        return self.COMMAND_TEMPLATE.format(
            executable=self.executable,
            name=application.name,
            options=" ".join(options),
        )

    def call_dumpdata(self, application, destination=None, indent=None,
                      extra_excludes=None):
        """
        Programmatically use the Django ``dumpdata`` command to dump application.

        TODO: Rename to "call"

        Arguments:
            application (ApplicationModel):

        Keyword Arguments:
            destination (Pathlib):
            indent (integer):
            extra_excludes (list):

        Returns:
            string: A JSON payload of call results. On default, this is the JSON
            output from dumpdata. However if destination has been given, dumpdata has
            written output to a file and so the returned JSON will just be a
            dictionnary with an item ``destination`` with written file path.
        """
        options = application.as_options()

        models = options.pop("models")
        filename = options.pop("filename")

        # Build args for command
        if destination:
            options["output"] = destination / filename

        if indent:
            options["indent"] = indent

        options["exclude"] = self.merge_excludes(
            options.pop("excludes"),
            extra_excludes
        )

        self.logger.info("Dumping data for application '{}'".format(application.name))

        # Execute command without output guided to string buffer
        out = StringIO()
        management.call_command(self.COMMAND_NAME, models, stdout=out, **options)

        # If the file has a destination, write to the FS, write the destination path
        # onto the application object
        if destination:
            out.close()
            application._written = destination / filename
            return json.dumps({"destination": str(application._written)})

        # No destination to write just write it into the string buffer
        content = out.getvalue()
        out.close()

        return content


class LoadDataSerializerAbstract:
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


class DumpDataSerializer(DumpDataSerializerAbstract):
    """
    Concrete basic implementation for ``DumpStorageAbstract``.

    Keyword Arguments:
        executable (string): A path to prefix commands, commonly the path to
            django-admin (or equivalent). This path will suffixed with a single space
            to ensure separation with command arguments.
        logger (object):
    """
    def __init__(self, executable=None, logger=None):
        self.executable = executable + " " if executable else ""
        self.logger = logger or NoOperationLogger()


class LoadDataSerializer(LoadDataSerializerAbstract):
    """
    Concrete basic implementation for ``LoadDataSerializerAbstract``.

    Keyword Arguments:
        executable (string): A path to prefix commands, commonly the path to
            django-admin (or equivalent). This path will suffixed with a single space
            to ensure separation with command arguments.
        logger (object):
    """
    def __init__(self, executable=None, logger=None):
        self.executable = executable + " " if executable else ""
        self.logger = logger or NoOperationLogger()
