import json
from pathlib import Path
from io import StringIO

from django.core import management

from ..utils.loggers import NoOperationLogger


class DumpDataSerializerAbstract:
    """
    Django dump serializer is in charge to serialize applications with Django dumpdata
    methods.

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
        Build command line to dump application.

        Arguments:
            application (ApplicationModel):

        Keyword Arguments:
            destination (Pathlib):
            indent (integer):
            extra_excludes (list):

        Returns:
            string:
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
        Programmatically use the Django dumpdata command to dump application.

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
        data = application.as_options()

        models = data.pop("models")
        filename = data.pop("filename")

        if destination:
            data["output"] = destination / filename

        if indent:
            data["indent"] = indent

        data["exclude"] = self.merge_excludes(data.pop("excludes"), extra_excludes)

        self.logger.info("Dumping data for application '{}'".format(application.name))

        out = StringIO()
        management.call_command(self.COMMAND_NAME, models, stdout=out, **data)

        if destination:
            out.close()
            return json.dumps({"destination": str(destination / filename)})

        content = out.getvalue()
        out.close()

        return content


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
