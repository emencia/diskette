from ...utils import versionning


class BaseHandler:
    """
    Base handler implements shared methods for all handlers.

    This relies on ``logger`` attribute that is not provided here. The logger object
    should be one of compatible classes from ``diskette.utils.loggers``.
    """
    def log_diskette_version(self):
        print()
        print()
        print(versionning.get_package_version())
        print()
        print()
        self.logger.debug(
            "{pkgname}=={version}".format(**versionning.get_package_version())
        )
