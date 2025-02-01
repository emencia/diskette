import json
from pathlib import Path
from io import StringIO

from django.core import management
from django.template.defaultfilters import filesizeformat

from ...utils.loggers import NoOperationLogger


class DumpdataSerializerAbstract:
    """
    Dump data serializer is in charge to serialize applications with Django dumpdata
    command.

    For now, this is JSON format only, 'format' option may be implemented later.
    """
    COMMAND_NAME = "dumpdata"
    COMMAND_TEMPLATE = "{executable}{cmd} {options}"

    def get_command_name(self, application):
        """
        Return effective command name to use.

        Either the application defines a custom command or this will be the default one
        from ``DumpdataSerializerAbstract.COMMAND_NAME``.

        Arguments:
            application (ApplicationConfig): Application object.

        Returns:
            string: Command name.
        """
        return getattr(application, "dump_command", None) or self.COMMAND_NAME

    def command(self, application, destination=None, indent=None):
        """
        Build a command line to use ``dumpdata``.

        Arguments:
            application (ApplicationConfig): Application object.

        Keyword Arguments:
            destination (Path): The file path where to write dumped data.
            indent (integer): Indentation level in data dumps.

        Returns:
            string: Command line to dump application datas.
        """
        options = []

        if indent:
            options.append("--indent={}".format(indent))

        if application.models:
            options.append(" ".join(application.models))

        if application.natural_foreign:
            options.append("--natural-foreign")

        if application.natural_primary:
            options.append("--natural-primary")

        if application.use_base_manager:
            options.append("--all")

        if application.is_drain:
            options.append(" ".join([
                "--exclude {}".format(item)
                for item in application.excludes
            ]))

        if destination:
            options.append("--output={}".format(
                str(Path(destination) / application.filename)
            ))

        cmd = self.get_command_name(application)

        return self.COMMAND_TEMPLATE.format(
            cmd=cmd,
            executable=self.executable,
            name=application.name,
            options=" ".join(options),
        )

    def call(self, application, destination=None, indent=None, traceback=False,
             check=False):
        """
        Programmatically use the Django ``dumpdata`` command to dump application.

        Arguments:
            application (ApplicationConfig): Application object.

        Keyword Arguments:
            destination (Path): The file path where to write dumped data.
            indent (integer): Indentation level in data dumps.
            traceback (boolean): If enabled, Django will output the full traceback when
                a dump raise an error. On default this is disabled and Django will
                silently hide exception tracebacks.
            check (boolean): Perform operations without writing or querying anything.

        Returns:
            string: A JSON payload of call results. On default, this is the JSON
                output from dumpdata. However if destination has been given, dumpdata
                has written output to a file and so the returned JSON will just be a
                dictionnary with an item ``destination`` with written file path.
        """
        options = application.as_options()

        models = options.pop("models")
        filename = options.pop("filename")
        use_base_manager = options.pop("use_base_manager")

        # Build args for command
        if destination:
            options["output"] = destination / filename

        if indent:
            options["indent"] = indent

        if use_base_manager:
            self.logger.debug("- Custom model manager is disabled")
            options["all"] = use_base_manager

        # Diskette never use 'excludes' for common applications
        excludes = options.pop("excludes")
        if application.is_drain:
            options["exclude"] = excludes

        if traceback:
            options["traceback"] = True

        self.logger.info("Dumping data for application '{}'".format(application.name))
        if models:
            self.logger.debug("- Including: {}".format(", ".join(models)))
        if excludes:
            self.logger.debug("- Excluding: {}".format(", ".join(excludes)))

        if check:
            return {"models": models, "options": options}

        # Execute command without output guided to string buffer
        out = StringIO()
        management.call_command(
            self.get_command_name(application),
            models,
            stdout=out,
            **options
        )

        # If the file has a destination, write to the FS, write the destination path
        # onto the application object
        if destination:
            out.close()
            application._written = options["output"]
            self.logger.debug("- Written file: {name} ({size})".format(
                name=filename,
                size=filesizeformat(options["output"].stat().st_size),
            ))
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
        logger (object): Instance of a logger object to use. Logger object must
            implement common logging message methods (like error, info, etc..). See
            ``diskette.utils.loggers`` for available loggers. If not given, a dummy
            logger will be used that ignores any messages and won't output anything.
    """
    def __init__(self, executable=None, logger=None):
        self.executable = executable + " " if executable else ""
        self.logger = logger or NoOperationLogger()
