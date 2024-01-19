import datetime
import json
import shutil
import tarfile
import tempfile
from pathlib import Path

from django.template.defaultfilters import filesizeformat

from ..exceptions import (
    ApplicationModelError, ApplicationRegistryError, DumpManagerError
)
from ..utils.filesystem import directory_size
from ..utils.lists import get_duplicates
from ..utils.loggers import NoOperationLogger

from .models import ApplicationModel, ApplicationDrainModel
from .serializers import DumpDataSerializerAbstract
from .storages import DumpStorageAbstract


class DumpLoader(DumpStorageAbstract, DumpDataSerializerAbstract):
    """
    Dump loader

    Keyword Arguments:
        logger (object):
    """
    MANIFEST_FILENAME = "manifest.json"
    TEMPDIR_PREFIX = "diskette_"

    def __init__(self, basepath=None, logger=None):
        self.basepath = basepath or Path.cwd()
        self.logger = logger or NoOperationLogger()

    def open(self, archive_path):
        """
        Extract archive files in a temporary directory.

        Arguments:
            archive_path (Path): A Path object to the archive to open.

        Returns:
            Path: The temporary directory where archive files have been extracted.
        """
        destination_tmpdir = Path(tempfile.mkdtemp(prefix=self.TEMPDIR_PREFIX))

        # Extract everything in temporary directory
        with tarfile.open(archive_path, "r:gz") as archive:
            archive.extractall(destination_tmpdir)

        # Remove archive
        # TODO: An option should allow to keep archive file but with a warning message
        # with its path
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
        manifest["datas"] = [Path(v) for v in manifest["datas"]]
        manifest["storages"] = [Path(v) for v in manifest["storages"]]

        return manifest

    def deploy_storages(self, extracted, manifest, destination):
        """
        Deploy storages directories in given destination

        Returns:
            list: List of tuple with source & destination paths for deployed storage.
        """
        deployed = []

        for dump_path in manifest["storages"]:
            storage_source = extracted / dump_path
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
                shutil.rmtree(storage_destination.parent)

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

    def deploy(self, archive_path, storages_destination):
        """
        Load archive and deploy its content.

        1. extractall to a tmp dir
        2. remove archive once extraction is over
        3. read manifest and increase it with the tmp dir path to use to get files
        4. restore dump data & files
        5. remove temporary directory

        Arguments:
            archive_path (Path): The tarball archive to open and extract dumps.
            storages_destination (Path): Destination where to deploy all storage
                directories.

        Returns:
            list:
        """
        tmpdir = self.open(archive_path)
        manifest = self.get_manifest(tmpdir)

        print()
        print(manifest)

        for dump in manifest["datas"]:
            print("- Should loaddata with:", tmpdir / dump)

        self.deploy_storages(tmpdir, manifest, storages_destination)

        return
