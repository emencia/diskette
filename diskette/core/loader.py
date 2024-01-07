import datetime
import json
import shutil
import tarfile
import tempfile
from pathlib import Path

from ..exceptions import (
    ApplicationModelError, ApplicationRegistryError, DumpManagerError
)
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

    def __init__(self, logger=None):
        self.logger = logger or NoOperationLogger()

    def open(self, archive_path):
        """
        TODO: Open archive, extract file in temp, read manifest
        """
        destination_tmpdir = Path(tempfile.mkdtemp(prefix=self.TEMPDIR_PREFIX))

        # Extract everything in temporary directory
        with tarfile.open(archive_path, "r:gz") as archive:
            archive.extractall(destination_tmpdir)

        # Remove archive
        archive_path.unlink()

        return destination_tmpdir

    def get_manifest(self, path):
        """
        Search for manifest file in given path, validate it and return it
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

        return manifest

    def deploy(self, archive_path, destination):
        """
        Load archive and deploy its content.

        1. extractall to a tmp dir
        2. remove archive once extraction is over
        3. read manifest and increase it with the tmp dir path to use to get files
        4. restore dump data & files
        5. remove temporary directory

        Arguments:
            path (Path):

        Returns:
            list:
        """
        tmpdir = self.open(archive_path)
        manifest = self.get_manifest(tmpdir)

        return
