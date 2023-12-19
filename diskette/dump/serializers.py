import json
from io import StringIO

from django.core import management


class DjangoDumpDataSerializer:
    """
    Django dump serializer is in charge to serialize applications with Django dumpdata
    methods.

    For now, this is JSON format only, 'format' option may come later.
    """
    COMMAND_NAME = "dumpdata"
    COMMAND_TEMPLATE = "{executable}dumpdata {options}"

    def __init__(self, executable=None):
        self.executable = executable + " " if executable else ""

    def command(self, application, destination=None, indent=None):
        """
        Build command line to dump application.

        Arguments:
            application (ApplicationModel):

        Keyword Arguments:
            destination (Pathlib):
            indent (integer):

        Returns:
            string:
        """
        options = []

        if indent:
            options.append("--indent={}".format(indent))

        options.append(" ".join(application.models))

        if application.natural_foreign:
            options.append("--natural-foreign")

        if application.natural_primary:
            options.append("--natural-primary")

        if application.exclude:
            options.append(" ".join([
                "--exclude {}".format(item)
                for item in application.exclude
            ]))

        if destination:
            options.append("--output={}".format(
                str(destination / application.filename)
            ))

        return self.COMMAND_TEMPLATE.format(
            executable=self.executable,
            name=application.name,
            options=" ".join(options),
        )

    def call(self, application, destination=None, indent=None):
        """
        Programmatically use the Django dumpdata command to dump application.

        Arguments:
            application (ApplicationModel):

        Keyword Arguments:
            destination (Pathlib):
            indent (integer):

        Returns:
            string: A JSON payload of call results. On default, this is the JSON
            output from dumpdata. However if destination has been given, dumpdata has
            written output to a file and so the returned JSON will just be a
            dictionnary with an item ``destination`` with written file path.
        """
        data = application.as_dict()

        models = data.pop("models")
        filename = data.pop("filename")

        if destination:
            data["output"] = destination / filename

        if indent:
            data["indent"] = indent

        out = StringIO()
        management.call_command(self.COMMAND_NAME, models, stdout=out, **data)

        if destination:
            out.close()
            return json.dumps({"destination": str(destination / filename)})

        return out.getvalue()
