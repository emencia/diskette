import logging

from django.core.management.base import CommandError

from ..exceptions import DisketteError
from .. import __pkgname__


class NoOperationLogger:
    """
    A fake logger which don't do anything, given messages to logging method just fall
    into void except for ``critical`` which raise the ``DisketteError`` exception.
    """
    def __init__(self, *args, **kwargs):
        pass

    def debug(self, msg):
        pass

    def info(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        pass

    def critical(self, msg):
        raise DisketteError(msg)


class LoggingOutput:
    """
    Basic output interface which use Python logging module.

    Mostly used in tests.
    """
    def __init__(self, *args, **kwargs):
        self.log = logging.getLogger(__pkgname__)

    def debug(self, msg):
        self.log.debug(msg)

    def info(self, msg):
        self.log.info(msg)

    def warning(self, msg):
        self.log.warning(msg)

    def error(self, msg):
        self.log.error(msg)

    def critical(self, msg):
        """
        Critical error is assumed to be a breaking event.
        """
        raise DisketteError(msg)


class DjangoCommandOutput:
    """
    Output interface which use the Django stdout and style interface.

    Keyword Arguments:
        command (django.core.management.base.BaseCommand): The Django command which
            have the ``stdout`` and ``style`` attributes. This is required.
        verbosity (integer): As defined from Django ``django-admin`` documentation,
            this specifies the amount of notification and debug information that a
            command should print to the console.

            * 0 means no output (no debug, no info, no warning);
            * 1 means normal output (default) (no debug);
            * 2 means verbose output;
            * 3 means very verbose output.

            There is actually no logging message method that depends from level 3 and
            so it won't have any additional effect than level 2.

            Errors are always printed.
        msg_buffer (io.StringIO): Buffer to store each messages, on default there is no
            buffer.
    """
    def __init__(self, *args, **kwargs):
        self.command = kwargs.get("command")
        self.verbosity = kwargs.get("verbosity", 1)
        self.msg_buffer = kwargs.get("msg_buffer", None)

    def fill_buffer(self, msg):
        if self.msg_buffer is not None:
            self.msg_buffer.write(str(msg) + "\n")

    def debug(self, msg):
        if self.verbosity > 1:
            self.command.stdout.write(str(msg))
            self.fill_buffer(msg)

    def info(self, msg):
        if self.verbosity > 0:
            self.command.stdout.write(
                self.command.style.SUCCESS(str(msg))
            )
            self.fill_buffer(msg)

    def warning(self, msg):
        if self.verbosity > 0:
            self.command.stdout.write(
                self.command.style.WARNING(str(msg))
            )
            self.fill_buffer(msg)

    def error(self, msg):
        self.command.stdout.write(
            self.command.style.ERROR(str(msg))
        )
        self.fill_buffer(msg)

    def critical(self, msg):
        """
        Critical error is assumed to be a breaking event but buffer is still filled
        correctly.
        """
        self.fill_buffer(msg)

        raise CommandError(str(msg))
