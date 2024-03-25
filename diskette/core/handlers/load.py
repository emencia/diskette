from pathlib import Path

from django.conf import settings

from ..loader import Loader
from ...utils.http import is_url


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
        Shortand to convert string path to a Path object for local archive file.

        Arguments:
            path (string or Path): The path to convert if elligible.

        Returns:
            string or Path: If given path is not an URL this returns a Path object else
                it returns given path unchanged as a string.
        """
        return path if is_url(path) else Path(path)

    def get_checksum(self, checksum):
        """
        Shortand to switch checksum value.

        Arguments:
            checksum (object): A string for a checksum or a boolean.

        Returns:
            Path: If checksum is equal to "no" this returns False to disable checksum
            creation. Any other value is returned without change.
        """
        if checksum == "no":
            return False

        return checksum

    def get_download_destination(self, path):
        """
        Shortand to convert string path to a Path object for downloaded archive
        destination.

        Arguments:
            path (string or Path): The string path to convert.

        Returns:
            Path: Path object.
        """
        return path if not path else Path(path)

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
             no_storages=False, download_destination=None, keep=False, checksum=None):
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
            no_data (boolean): Disable loading application datas from archive.
            no_storages (boolean): Disable loading media storages from archive.
            download_destination (Path): A path where to write downloaded archive file.
                If not given, the archive file will be written as
                ``diskette_downloaded_archive.tar.gz`` into the current working
                directory. This argument is useless with local archive file.
            keep (boolean): If enabled, the archive is not automatically removed once
                loading if finished. On default this is disabled and the archive is
                removed.
            checksum (object): Manage if archive is checksumed or not depending value:

                * If ``None``: Checksum is done and just output to logs;
                * If ``True``: Checksum is done and just output to logs;
                * If ``False``: No checksum are done or compared;
                * Any other value is assumed to be a string for a checksum to compare.
                  Then a checksum is done on archive and compared to the given one, if
                  comparaison fails it results to a critical error.

        Returns:
            dict: Statistics of deployed storages and datas.
        """
        self.logger.info("=== Starting restoration ===")

        with_data = not no_data
        with_storages = not no_storages

        if not with_data and not with_storages:
            self.logger.critical(
                "Data and storages dumps can not be both disabled. At least one dump "
                "type must be enabled."
            )

        archive_path = self.get_archive_path(archive_path)
        checksum = self.get_checksum(checksum)
        storages_basepath = self.get_storages_basepath(storages_basepath)
        download_destination = self.get_download_destination(download_destination)

        manager = Loader(logger=self.logger)

        # Validate configurations
        manager.validate()

        # Validate configurations
        stats = manager.deploy(
            archive_path,
            storages_basepath,
            with_data=with_data,
            with_storages=with_storages,
            download_destination=download_destination,
            keep=keep,
            checksum=checksum,
        )

        return stats
