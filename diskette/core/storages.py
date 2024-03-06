import fnmatch
import os
from pathlib import Path

from ..exceptions import DumperError
from ..utils.loggers import NoOperationLogger


class StorageMixin:
    """
    Storage manager is in charge to collect storage file paths.

    .. Note::
        ``self.storages_basepath`` value  determine if storages are valid (they must be
        a children of it) and how they will be stored in archive since they are
        made relative from the ``storages_basepath``
    """
    def validate_storages(self):
        """
        Validate every storage path defined from settings.

        A storage path must be a Path object, exists on filesystem and must be a
        directory.

        Raises:
            DumperError: In case of error with a storage path.
        """
        for storage in self.storages:
            if not isinstance(storage, Path):
                raise DumperError(
                    "Storage path is not a 'pathlib.Path' object: {}".format(storage)
                )

            if not storage.exists():
                raise DumperError(
                    "Storage path does not exist: {}".format(storage)
                )

            if not storage.is_dir():
                raise DumperError(
                    "Storage path is not a directory: {}".format(storage)
                )

            try:
                storage.relative_to(self.storages_basepath)
            except ValueError:
                raise DumperError(
                    "Storage must be a child of: {}".format(self.storages_basepath)
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
                        yield path, path.relative_to(self.storages_basepath)


class StorageManager(StorageMixin):
    """
    Concrete basic implementation for ``DumpStorageAbstract``.

    Keyword Arguments:
        storages_basepath (Path): Basepath for reference in some path resolution.
            Currently used by storage dump to make relative path for storage files.
            On default this is based on current working directory. If given, the
            storage paths must be in the same leaf else this will be an error.
        storages (list): A list of storage Path objects.
        storages_excludes (list): A list of patterns to exclude storage files from
            dump.
        logger (object):
    """
    def __init__(self, storages_basepath=None, storages=None, storages_excludes=None,
                 logger=None):
        self.storages_basepath = storages_basepath or Path.cwd()
        self.logger = logger or NoOperationLogger()
        self.storages = storages or []
        self.storages_excludes = storages_excludes or []
