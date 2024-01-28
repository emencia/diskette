"""
Specific application exceptions.
"""


class DisketteBaseException(Exception):
    """
    Exception base.

    You should never use it directly except for test purpose. Instead make or
    use a dedicated exception related to the error context.
    """
    pass


class DisketteError(DisketteBaseException):
    """
    Basic error without specific components.
    """
    pass


class ApplicationConfigError(DisketteBaseException):
    """
    For an error from model ApplicationConfig.
    """
    pass


class DumperError(DisketteBaseException):
    """
    For an error from dump manager.
    """
    pass


class ApplicationRegistryError(DisketteBaseException):
    """
    For an error during validation of application model objects.

    Attribute ``error_messages`` contains a dict of applications error messages.

    Keyword Arguments:
        error_messages (dict): A dictionnary of all application errors. It
            won't output as exception message from traceback, you need to exploit it
            yourself if needed.
    """
    def __init__(self, *args, **kwargs):
        self.error_messages = kwargs.pop("error_messages", [])
        self.message = self.get_payload_message(*args)
        super().__init__(*args, **kwargs)

    def get_payload_message(self, *args):
        if self.error_messages:
            return "Some defined applications have errors: {}".format(
                ", ".join([k for k, v in self.error_messages.items()])
            )
        elif len(args) > 0:
            return args[0]

        return "Unexpected error"

    def get_payload_details(self):
        if self.error_messages:
            return [
                v
                for k, v in self.error_messages.items()
            ]

        return []

    def __str__(self):
        return self.message
