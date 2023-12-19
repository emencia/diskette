"""
Specific application exceptions.
"""


class DjangoDrDumpBaseException(Exception):
    """
    Exception base.

    You should never use it directly except for test purpose. Instead make or
    use a dedicated exception related to the error context.
    """
    pass


class ApplicationModelError(DjangoDrDumpBaseException):
    """
    For an error from model ApplicationModel.
    """
    pass


class DumpManagerError(DjangoDrDumpBaseException):
    """
    For an error from dump manager.
    """
    pass
