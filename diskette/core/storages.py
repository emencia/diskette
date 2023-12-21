import fnmatch
import os
from pathlib import Path

from ..exceptions import DumpManagerError
from ..utils.loggers import NoOperationLogger


class DumpStorageAbstract:
    """
    Storage manager is in charge to collect storage file paths.
    """
    def validate_storages(self):
        """
        Validate every storage path defined from settings.

        A storage path must be a Path object, exists on filesystem and must be a
        directory.

        Raises:
            DumpManagerError: In case of error with a storage path.
        """
        for storage in self.storages:
            if not isinstance(storage, Path):
                raise DumpManagerError(
                    "Storage path is not a 'pathlib.Path' object: {}".format(storage)
                )

            if not storage.exists():
                raise DumpManagerError(
                    "Storage path does not exist: {}".format(storage)
                )

            if not storage.is_dir():
                raise DumpManagerError(
                    "Storage path is not a directory: {}".format(storage)
                )

    def is_allowed_path(self, path):
        """
        Check if given path match is allowed to be collected depending it match or not
        any exclude patterns.
        """
        for rule in self.storages_excludes:
            if fnmatch.fnmatch(path, rule):
                return False

        return True

    def iter_storages_files(self, allow_excludes=True):
        """
        Returns
            iterator:
        """
        for storage in self.storages:
            # Recursively walk through storage path
            for root, dirs, files in os.walk(storage):
                base = Path(root)
                # Only care about files
                for item in files:
                    path = base / item
                    # Check relative "in-storage" file path against excluding rules
                    if (
                        not allow_excludes or
                        self.is_allowed_path(path.relative_to(storage))
                    ):
                        yield path, path.relative_to(self.basepath)


class DumpStorage(DumpStorageAbstract):
    """
    Concrete basic implementation for ``DumpStorageAbstract``.

    Keyword Arguments:
        basepath (Path): Basepath for reference in some path resolution. Currently
            used by storage dump to make relative path for storage files. On default
            this is based on current working directory. If given, the storage paths
            must be in the same leaf else this will be an error.
        storages (list): A list of storage Path objects.
        storages_excludes (list): A list of patterns to exclude storage files from dump.
        logger (object):
    """
    def __init__(self, basepath=None, storages=None, storages_excludes=None,
                 logger=None):
        self.basepath = basepath or Path.cwd()
        self.logger = logger or NoOperationLogger()
        self.storages = storages or []
        self.storages_excludes = storages_excludes or []
