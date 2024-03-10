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
        """
        Shortand to convert string path to a Path object.

        Arguments:
            path (string or Path): The path to convert.

        Returns:
            Path: The path.
        """
        return Path(path)

    def get_storages_basepath(self, path=None):
        """
        Get the storage basepath to use when deploying storages.

        Storage basepath can not be empty, a critical error object is raised from
        logger if the basepath resolve to an empty value. However the basepath does not
        need to exists (but it would lead to unexpected errors).

        Keyword Arguments:
            path (Path): Path to use as the storage basepath. If not given, the value
                from ``settings.DISKETTE_LOAD_STORAGES_PATH`` is used.

        Returns:
            Path: Storage basepath.
        """
        path = path or settings.DISKETTE_LOAD_STORAGES_PATH

        if not path:
            self.logger.critical("Storages destination path can not be an empty value")

        self.logger.debug(
            "- Storages contents will be restored into: {}".format(path)
        )

        return path

    def load(self, archive_path, storages_basepath=None, no_data=False,
             no_storages=False, keep=False):
        """
        Proceed to load and deploy archive contents.

        Keyword Arguments:
            archive_filename (string): Custom archive filename to use instead of the
                default one. Your custom filename must end with ``.tar.gz``. Default
                filename is ``diskette[_data][_storages].tar.gz`` (parts depend from
                options).
            storages_basepath (Path): Basepath for reference in some path resolution.
                Currently used by storage dump to make relative path for storage files.
                On default this is based on current working directory. If given, the
                storage paths must be in the same leaf else this will be an error.
            no_data (boolean): Disable dump of application datas.
            no_storages (boolean): Disable dump of media storages.
            keep (boolean): If enabled, the archive is not automatically removed once
                loading if finished. On default this is disabled and the archive is
                removed.

        Returns:
            dict: Statistics of deployed storages and datas.
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
            keep=keep,
        )

        return stats
