import json
import shutil
import tarfile
import tempfile
from pathlib import Path

from django.template.defaultfilters import filesizeformat

from ..utils.filesystem import directory_size
from ..utils.loggers import NoOperationLogger

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

    def __init__(self, logger=None):
        self.logger = logger or NoOperationLogger()

    def open(self, archive_path, keep=False):
        """
        Extract archive files in a temporary directory.

        .. Warning::
            Using this method, you are responsible to remove the temporary directory
            once you are done with it. Your code must be safe about it and remove it
            even when your code fails or you will produce a lot of remaining temporary
            directories.

        Arguments:
            archive_path (Path): A Path object to the archive to open.
            keep (boolean): Archive won't be removed from filesystem if True, else the
                archive file is removed once it have been extracted.

        Returns:
            Path: The temporary directory where archive files have been extracted.
        """
        if (
            isinstance(archive_path, str) and
            archive_path.startswith(("http://", "https://"))
        ):
            # TODO: Download file with request in a temporary path, to remove once
            # extracted
            # archive_path = Path(..)
            raise NotImplementedError("Loader does not support archive URL yet.")

        destination_tmpdir = Path(tempfile.mkdtemp(prefix=self.TEMPDIR_PREFIX))

        # Extract everything in temporary directory
        with tarfile.open(archive_path, "r:gz") as archive:
            archive.extractall(destination_tmpdir)

        if not keep:
            archive_path.unlink()

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

    def deploy(self, archive_path, storages_destination, with_data=True,
               with_storages=True, keep=False):
        """
        Load archive and deploy its content.

        Arguments:
            archive_path (Path): The tarball archive to open and extract dumps.
            storages_destination (Path): Destination where to deploy all storage
                directories.

        Keyword Arguments:
            with_data (boolean): Enable application datas loading.
            with_storages (boolean): Enabled media storages loading.
            keep (boolean): Archive won't be removed from filesystem if True, else the
                archive file is removed once it have been extracted.

        Returns:
            dict: Statistics of deployed storages and datas.
        """
        tmpdir = self.open(archive_path, keep=keep)

        try:
            manifest = self.get_manifest(tmpdir)
            stats = {
                "storages": self.deploy_storages(
                    tmpdir,
                    manifest,
                    storages_destination
                ),
                "datas": self.deploy_datas(tmpdir, manifest),
            }
        finally:
            if tmpdir.exists():
                shutil.rmtree(tmpdir)

        return stats
