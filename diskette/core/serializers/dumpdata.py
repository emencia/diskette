import json
from pathlib import Path
from io import StringIO

from django.core import management

from ...utils.loggers import NoOperationLogger


class DumpdataSerializerAbstract:
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

    def command(self, application, destination=None, indent=None, extra_excludes=None):
        """
        Build command line to use ``dumpdata``.

        Arguments:
            application (ApplicationConfig):

        Keyword Arguments:
            destination (Pathlib):
            indent (integer):
            extra_excludes (list):

        Returns:
            string: Command line to run a dumpdata job.
        """
        options = []

        # TODO: Remove this since it involves a different behavior with model manager
        # to get everything we just have to give no label at all
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

    def call(self, application, destination=None, indent=None, extra_excludes=None):
        """
        Programmatically use the Django ``dumpdata`` command to dump application.

        Arguments:
            application (ApplicationConfig):

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


class DumpdataSerializer(DumpdataSerializerAbstract):
    """
    Concrete basic implementation for ``StorageMixin``.

    Keyword Arguments:
        executable (string): A path to prefix commands, commonly the path to
            django-admin (or equivalent). This path will suffixed with a single space
            to ensure separation with command arguments.
        logger (object):
    """
    def __init__(self, executable=None, logger=None):
        self.executable = executable + " " if executable else ""
        self.logger = logger or NoOperationLogger()
