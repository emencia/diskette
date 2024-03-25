import json
import shutil
import tarfile
import tempfile
import requests
from pathlib import Path

from django.conf import settings
from django.template.defaultfilters import filesizeformat

from ..utils.filesystem import directory_size
from ..utils.loggers import NoOperationLogger
from ..utils import hashs
from ..utils.http import is_url

from .serializers import LoaddataSerializerAbstract
from .storages import StorageMixin


class Loader(StorageMixin, LoaddataSerializerAbstract):
    """
    Dump loader opens a Diskette archive to deploy its data and storage contents.

    Keyword Arguments:
        logger (object): Instance of a logger object to use. Logger object must
            implement common logging message methods (like error, info, etc..). See
            ``diskette.utils.loggers`` for available loggers. If not given, a dummy
            logger will be used that ignores any messages and won't output anything.
    """
    MANIFEST_FILENAME = "manifest.json"
    TEMPDIR_PREFIX = "diskette_"
    DOWNLOAD_FILENAME = "diskette_downloaded_archive.tar.gz"

    def __init__(self, logger=None):
        self.logger = logger or NoOperationLogger()

    def download_archive(self, url, destination=None):
        """
        Download archive from given URL into destination directory.

        Arguments:
            url (string): The archive URL to download.

        Keyword Arguments:
            destination (Path): A path where to write downloaded archive file. If not
                given, the archive file will be written as
                ``diskette_downloaded_archive.tar.gz`` into the current working
                directory.

        Returns:
            Path: Path to downloaded archive file.
        """
        destination = destination or Path.cwd() / self.DOWNLOAD_FILENAME
        self.logger.info(
            "Downloading archive from '{}' to '{}'".format(url, destination)
        )

        request = requests.get(
            url,
            allow_redirects=settings.DISKETTE_DOWNLOAD_ALLOW_REDIRECT,
            timeout=settings.DISKETTE_DOWNLOAD_TIMEOUT,
            stream=True
        )
        request.raise_for_status()

        # Use the chunk way to avoid retaining the whole file in memory
        with open(destination, "wb") as fd:
            for chunk in request.iter_content(
                chunk_size=settings.DISKETTE_DOWNLOAD_CHUNK
            ):
                fd.write(chunk)

        return destination

    def open(self, source, download_destination=None, keep=False, checksum=None):
        """
        Extract archive files in a temporary directory.

        .. Warning::
            Using this method, you are responsible to remove the temporary directory
            once you are done with it. Your code must be safe about it and remove it
            even when your code fails or you will produce a lot of remaining temporary
            directories.

        Arguments:
            source (Path): A Path object to the archive to open.

        Keyword Arguments:
            download_destination (Path): A path where to write downloaded archive file.
                If not given, the archive file will be written as
                ``diskette_downloaded_archive.tar.gz`` into the current working
                directory. This argument is useless with local archive file.
            keep (boolean): Archive won't be removed from filesystem if True, else the
                archive file is removed once it have been extracted.
            checksum (object): Manage if archive is checksumed or not depending value:

                * If ``None``: Checksum is done and just output to logs;
                * If ``True``: Checksum is done and just output to logs;
                * If ``False``: No checksum are done or compared;
                * Any other value is assumed to be a string for a checksum to compare.
                  Then a checksum is done on archive and compared to the given one, if
                  comparaison fails it results to a critical error.

        Returns:
            Path: The temporary directory where archive files have been extracted.
        """
        archive = source
        if is_url(source):
            archive = self.download_archive(source, destination=download_destination)

        # The temporary directory where to extract archive content
        destination_tmpdir = Path(tempfile.mkdtemp(prefix=self.TEMPDIR_PREFIX))

        # Perform checksum if not explicitely disabled
        if checksum is not False:
            archive_checksum = hashs.file_checksum(archive)
            self.logger.debug(
                "Archive checksum: {}".format(archive_checksum)
            )
            # Compare checksums if any
            if checksum and checksum is not True:
                if archive_checksum != checksum:
                    self.logger.critical(
                        "Checksums do not match. Your archive file is probably "
                        "corrupted."
                    )

        try:
            # Extract everything in temporary directory
            with tarfile.open(archive, "r:gz") as archive_fp:
                archive_fp.extractall(destination_tmpdir)
        except Exception as e:
            # Remove destination_tmpdir on extraction failure
            if destination_tmpdir.exists():
                shutil.rmtree(destination_tmpdir)
            # Then raise the exception
            raise e
        finally:
            # Remove archive if not required to be keeped
            if not keep:
                archive.unlink()

        return destination_tmpdir

    def get_manifest(self, path):
        """
        Search for manifest file in given path, validate it and return it.

        This raises an exception if manifest is invalid, the used exception class will
        depends from used logger.

        Arguments:
            path (Path): Path object to the directory where to search for the manifest
                file.

        Returns:
            dict: The manifest data.
        """
        manifest_path = path / self.MANIFEST_FILENAME
        if not manifest_path.exists():
            self.logger.critical(
                "Dump archive is invalid, it does not include manifest file "
                "'manifest.json'"
            )

        try:
            manifest = json.loads(manifest_path.read_text())
        except json.JSONDecodeError as e:
            self.logger.critical(
                "Dump archive is invalid, included manifest file has invalid JSON "
                "syntax: {}".format(str(e))
            )

        if "datas" not in manifest:
            self.logger.critical(
                "Dump archive is invalid, manifest does not include 'datas' field."
            )

        if "storages" not in manifest:
            self.logger.critical(
                "Dump archive is invalid, manifest does not include 'storages' field."
            )

        # Turn data file and storage items to Path objects
        manifest["datas"] = [Path(v) for v in manifest.get("datas") or []]
        manifest["storages"] = [Path(v) for v in manifest.get("storages") or []]

        return manifest

    def validate_datas(self):
        """
        Call validators from all enabled data dumps.

        .. Note::
            There is currently no validator needed.

        Returns:
            boolean: Always return True since there is nothing to validate actually.
        """
        return True

    def validate_storages(self):
        """
        Call validators from all enabled storages.

        .. Note::
            There is currently no validator needed.

        Returns:
            boolean: Always return True since there is nothing to validate actually.
        """
        return True

    def validate(self):
        """
        Call all validators
        """
        self.validate_datas()
        self.validate_storages()

    def deploy_storages(self, archive_dir, manifest, destination):
        """
        Deploy storages directories in given destination

        Arguments:
            archive_dir (Path): Path to directory where archive has been exracted.
            manifest (dict): The manifest data.
            destination (Path): Path to directory where to deploy storages.

        Returns:
            list: List of tuples for deployed storage with respectively source and
                destination paths.
        """
        deployed = []

        for dump_path in manifest["storages"]:
            storage_source = archive_dir / dump_path
            storage_destination = destination / dump_path

            # Create complete destination path structure if needed
            if not storage_destination.parent.exists():
                self.logger.debug(
                    "Creating storage parent directory: {}".format(
                        storage_destination.parent
                    )
                )
                storage_destination.parent.mkdir(parents=True)

            # Remove possible existing storage
            if storage_destination.exists():
                self.logger.debug(
                    "Removing previous storage version directory: {}".format(
                        storage_destination
                    )
                )
                shutil.rmtree(storage_destination)

            # Move storage dump to destination
            self.logger.info(
                "Restoring storage directory ({}): {}".format(
                    filesizeformat(directory_size(storage_source)),
                    dump_path
                )
            )
            shutil.move(storage_source, storage_destination)

            deployed.append((storage_source, storage_destination))

        return deployed

    def deploy_datas(self, archive_dir, manifest):
        """
        Deploy storages directories in given destination

        Arguments:
            archive_dir (Path): Path to directory where archive has been exracted.
            manifest (dict): The manifest data.

        Returns:
            list: List of tuples for deployed dumps with respectively source and
                loaddata output.
        """
        return [
            (dump.name, self.call(archive_dir / dump))
            for dump in manifest["datas"]
        ]

    def deploy(self, archive, storages_destination, with_data=True, with_storages=True,
               download_destination=None, keep=False, checksum=None):
        """
        Load archive and deploy its content.

        Arguments:
            archive (Path or string): The tarball archive to open and extract dumps. It
                may be either a Path to a local archive file or a string for an URL
                to download the archive.
            storages_destination (Path): Destination where to deploy all storage
                directories.

        Keyword Arguments:
            with_data (boolean): Enable application datas loading.
            with_storages (boolean): Enabled media storages loading.
            download_destination (Path): A path where to write downloaded archive file.
                If not given, the archive file will be written as
                ``diskette_downloaded_archive.tar.gz`` into the current working
                directory. This argument is useless with local archive file.
            keep (boolean): Archive won't be removed from filesystem if True, else the
                archive file is removed once it have been extracted.
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
        tmpdir = self.open(
            archive,
            download_destination=download_destination,
            keep=keep,
            checksum=checksum,
        )

        stats = {}
        try:
            manifest = self.get_manifest(tmpdir)

            if with_storages:
                stats["storages"] = self.deploy_storages(
                    tmpdir,
                    manifest,
                    storages_destination
                )

            if with_data:
                stats["datas"] = self.deploy_datas(tmpdir, manifest)
        finally:
            if tmpdir.exists():
                shutil.rmtree(tmpdir)

        return stats
