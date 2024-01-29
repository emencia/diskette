from pathlib import Path

from django.conf import settings

from ..loader import Loader


class LoadCommandHandler:
    """
    Abstraction layer between Loader and the management command, it holds getters
    to get and validate values for manager options and provide a shortand to
    dump or load contents with options.

    This relies on ``logger`` attribute that is not provided here. The logger object
    should be one of compatible classes from ``diskette.utils.loggers``.
    """

    def get_archive_path(self, path):
        return Path(path)

    def get_storages_basepath(self, path):
        path = path or settings.DISKETTE_LOAD_STORAGES_PATH

        if not path:
            self.logger.critical("Storages destination path can not be an empty value")

        self.logger.debug(
            "- Storages contents will be restored into: {}".format(path)
        )

        return path

    def load(self, archive_path, storages_basepath=None, no_data=False,
             no_storages=False):
        """
        Proceed to archive content loading.
        """
        self.logger.info("=== Starting restoration ===")

        archive_path = self.get_archive_path(archive_path)
        storages_basepath = self.get_storages_basepath(storages_basepath)

        with_data = not no_data
        with_storages = not no_storages

        if not with_data and not with_storages:
            self.logger.critical(
                "Data and storages dumps can not be both disabled. At least one dump "
                "type must be enabled."
            )

        manager = Loader(logger=self.logger)

        # Validate configurations
        manager.validate()

        # Validate configurations
        stats = manager.deploy(
            archive_path,
            storages_basepath,
            with_data=with_data,
            with_storages=with_storages,
        )

        return stats
