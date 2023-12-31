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


class DumpManager(DumpStorageAbstract, DumpDataSerializerAbstract):
    """
    Dump manager in in charge of storing application model objects, return serialized
    datas and storage files to dump them.

    .. Note::
        A drain is a specific application that is always processed after the standard
        applications, even if it has been defined between other standard applications.

    Keyword Arguments:
        executable (string): A path to prefix commands, commonly the path to
            django-admin (or equivalent). This path will suffixed with a single space
            to ensure separation with command arguments. This is only used with
            ``serialize_command``.
        basepath (Path): Basepath for reference in some path resolution. Currently
            used by storage dump to make relative path for storage files. On default
            this is based on current working directory. If given, the storage paths
            must be in the same leaf else this will be an error.
        storages (list): A list of storage Path objects.
        storages_excludes (list): A list of patterns to exclude storage files from dump.
        logger (object):
    """
    MANIFEST_FILENAME = "manifest.json"
    TEMPDIR_PREFIX = "diskette_"

    def __init__(self, apps, executable=None, basepath=None, storages=None,
                 storages_excludes=None, logger=None):
        self.basepath = basepath or Path.cwd()
        self.executable = executable + " " if executable else ""
        self.logger = logger or NoOperationLogger()
        self.storages = storages or []
        self.storages_excludes = storages_excludes or []

        self.apps = self.load(apps)

    def load(self, apps):
        """
        Load ApplicationModel objects from given Application datas.

        Arguments:
            apps (list):

        Returns:
            list:
        """
        objects = []
        drains = []

        # Check for duplicated name
        twices = list(get_duplicates([name for name, options in apps]))
        if twices:
            raise DumpManagerError(
                "There was some duplicate names from applications: {}".format(
                    ", ".join(twices)
                )
            )

        for name, options in apps:
            if options.pop("is_drain", False):
                drains.append(ApplicationDrainModel(name, **options))
            else:
                objects.append(ApplicationModel(name, **options))

        return objects + drains

    def get_involved_models(self, with_excluded=True):
        """
        Get all app models from application definitions.

        This method purpose is essentially to collect all models to exclude from drain.

        Keyword Arguments:
            with_excluded (boolean): If True, the excluded models are also returned for
                application which allows it with their ``allow_drain`` option. If False
                the excluded model won't be included. Default is True.

        Returns:
            list: List of application or model names.
        """
        models = []

        for app in self.apps:
            models.extend(app.models)
            # Consided application excluded model as involved also
            if with_excluded is True and app.allow_drain is True:
                # Append without duplicates
                models.extend([
                    item
                    for item in app.excludes
                    if item not in models
                ])

        return models

    def dump_options(self):
        """
        Build a dictionnary of options for each application.

        Keyword Arguments:
            name (boolean): To include or not the name into the dict.
            commented (boolean): To include or not the comments into the dict.

        Returns:
            list:
        """
        return [app.as_options() for app in self.apps]

    def payload(self):
        """
        Build a dictionnary of configuration payload for each application.

        Keyword Arguments:
            name (boolean): To include or not the name into the dict.
            commented (boolean): To include or not the comments into the dict.

        Returns:
            list:
        """
        return [app.as_config() for app in self.apps]

    def build_commands(self, destination=None, indent=None):
        """
        Build dumpdata command line for each application.

        Keyword Arguments:
            destination (string or Path):
            indent (integer):

        Returns:
            list:
        """
        return [
            (
                app.name,
                self.serialize_command(app, destination=destination, indent=indent)
            )
            for app in self.apps
            if app.is_drain is not True
        ] + [
            (
                app.name,
                self.serialize_command(
                    app,
                    destination=destination,
                    indent=indent,
                    extra_excludes=self.get_involved_models(
                        with_excluded=app.drain_excluded
                    ),
                )
            )
            for app in self.apps
            if app.is_drain is True
        ]

    def dump_data(self, destination=None, indent=None):
        """
        Call dumpdata command to dump each application data.

        Keyword Arguments:
            destination (string or Path):
            indent (integer):

        Returns:
            list:
        """
        return [
            (
                app.name,
                self.call_dumpdata(app, destination=destination, indent=indent)
            )
            for app in self.apps
            if app.is_drain is not True
        ] + [
            (
                app.name,
                self.call_dumpdata(
                    app,
                    destination=destination,
                    indent=indent,
                    extra_excludes=self.get_involved_models(
                        with_excluded=app.drain_excluded
                    ),
                )
            )
            for app in self.apps
            if app.is_drain is True
        ]

    def validate_applications(self):
        """
        Call validators from all enabled application model objects.
        """
        errors = {}

        # Collect all model errors
        for app in self.apps:
            try:
                app.validate()
            except ApplicationModelError as e:
                errors[app.name] = str(e)

        # Raise a single exception containing all collected errors
        if errors:
            raise ApplicationRegistryError(error_messages=errors)

    def format_tarball_filename(self, filename, with_data=False, with_storages=False):
        """
        Format tarball filename depending features.

        Keyword Arguments:
            filename (string): Filename to use instead. It must end with ``.tar.gz``.
                Filename format should be like ``diskette{features}.tar.gz`` where
                features pattern can include either ``_data``, ``_storages`` or both
                depending enabled dump kinds.
            with_data (boolean): Enable dump of application datas.
            with_storages (boolean): Enabled dump of media storages.

        Returns:
            string: Formatted filename with features.
        """
        filename_features = ""
        if with_data is True:
            filename_features += "_data"
        if with_storages is True:
            filename_features += "_storages"

        return filename.format(features=filename_features)

    def build_dump_manifest(self, destination, data_destination, with_data=True,
                            with_storages=True):
        """
        Build dump JSON manifest.
        """
        manifest_path = destination / self.MANIFEST_FILENAME
        manifest_path.write_text(
            json.dumps({
                "creation": datetime.datetime.now().isoformat(timespec="seconds"),
                "datas": [
                    str(dump.relative_to(destination))
                    for dump in data_destination.iterdir()
                    if with_data is True
                ],
                "storages": [
                    str(storage.relative_to(self.basepath))
                    for storage in self.storages
                    if with_storages is True
                ],
            })
        )

        return manifest_path

    def validate(self):
        """
        Call all validators
        """
        self.validate_applications()
        self.validate_storages()

    def make_tarball(self, destination, filename, with_data=True, with_storages=True,
                     with_storages_excludes=True, destination_chmod=0o644):
        """
        Check if given path match is allowed to be collected depending it match or not
        any exclude patterns.

        .. Note::
            Arguments 'with_data' and 'with_storages' can not be both disabled, at
            least one must be enabled else it is assumed as an error.

        Keyword Arguments:
            destination (Path): Directory where to write tarball file.
            filename (string): Custom tarball filename to use instead of the default
                one. Your custom filename must end with ``.tar.gz``. Default filename
                is ``diskette[_data][_storages].tar.gz`` (parts depend from options).
            with_data (boolean): Enable dump of application datas.
            with_storages (boolean): Enabled dump of media storages.
            with_storages_excludes (boolean): Enable usage of excluding patterns when
                collecting storages files.
            destination_chmod (integer): File permission to apply on tarball files and
                also on destination directory if it did not exists. Value must be in
                an octal notation, default is ``0o644``.

        Returns:
            Path: Written tarball file path.
        """
        if not with_data and not with_storages:
            raise DumpManagerError(
                "Arguments 'with_data' and 'with_storages' can not be both 'False'"
            )

        # Temporary directory where the manager will work
        destination_tmpdir = Path(tempfile.mkdtemp(prefix=self.TEMPDIR_PREFIX))

        # Build data dump destination path
        data_tmpdir = destination_tmpdir / "data"
        data_tmpdir.mkdir()

        # Dump data into temp directory
        if with_data is True:
            self.dump_data(destination=data_tmpdir)

        # Compute history/stats file
        manifest_path = self.build_dump_manifest(
            destination_tmpdir,
            data_tmpdir,
            with_data=with_data,
            with_storages=with_storages
        )

        # Build dump tarball paths
        tarball_filename = self.format_tarball_filename(
            filename,
            with_data=with_data,
            with_storages=with_storages
        )
        tarball_path = destination_tmpdir / tarball_filename
        tarball_destination = destination / tarball_filename

        # Then add everything to the tarball
        try:
            with tarfile.open(tarball_path, "w:gz") as tar:
                # Add data dumps dir
                if with_data is True:
                    self.logger.info("Appending data to the archive")
                    tar.add(data_tmpdir, arcname="data")
                    # Clear space from data dumps
                    shutil.rmtree(data_tmpdir)

                # Append collected storages files
                if with_storages is True:
                    self.logger.info("Appending storages to the archive")
                    for path, arcname in self.iter_storages_files(
                        allow_excludes=with_storages_excludes
                    ):
                        tar.add(path, arcname=arcname)

                # Append dump manifest
                tar.add(manifest_path, arcname=self.MANIFEST_FILENAME)

            # Create destination directory with the right permission if needed
            if not destination.exists():
                destination.mkdir(
                    mode=destination_chmod,
                    parents=True,
                    exist_ok=True
                )

            # Use shutil instead of Path.rename since the latter does not work well
            # with different devices
            shutil.move(tarball_path, tarball_destination)
            tarball_destination.chmod(destination_chmod)

        finally:
            # Always remove temporary working directory
            shutil.rmtree(destination_tmpdir)

        return tarball_destination
