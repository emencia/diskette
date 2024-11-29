import datetime
import json
import shutil
import tarfile
import tempfile
from pathlib import Path

from django.conf import settings
from django.template.defaultfilters import filesizeformat

from ..exceptions import (
    ApplicationConfigError, ApplicationRegistryError, DumperError
)
from ..utils import versionning
from ..utils.lists import get_duplicates, unduplicated_merge_lists
from ..utils.loggers import NoOperationLogger

from .applications import ApplicationConfig, DrainApplicationConfig
from .serializers import DumpdataSerializerAbstract
from .storages import StorageMixin


class Dumper(StorageMixin, DumpdataSerializerAbstract):
    """
    Dump manager is in charge of storing application model objects, return serialized
    datas and storage files to dump them.

    Arguments:
        apps (list): List of dictionnaries, each dictionnary is a data dump definition.
            Each dictionnary will be turned to ``DrainApplicationConfig`` or
            ``ApplicationConfig`` object, depending it is a drain or not.

    Keyword Arguments:
        executable (string): A path to prefix commands, commonly the path to
            django-admin (or equivalent). This path will suffixed with a single space
            to ensure separation with command arguments. This is only used with
            ``command``.
        storages_basepath (Path): Basepath for reference in some path resolution.
            Currently used by storage dump to make relative path for storage files.
            On default this is based on current working directory. If given, the
            storage paths must be in the same leaf else this will be an error.
        storages (list): A list of storage Path objects.
        storages_excludes (list): A list of patterns to exclude storage files from
            dump.
        indent (integer): Indentation level in data dumps. If not given, dumps won't
            be indented.
        logger (object): Instance of a logger object to use. Logger object must
            implement common logging message methods (like error, info, etc..). See
            ``diskette.utils.loggers`` for available loggers. If not given, a dummy
            logger will be used that ignores any messages and won't output anything.
    """
    MANIFEST_FILENAME = "manifest.json"
    TEMPDIR_PREFIX = "diskette_"

    def __init__(self, apps, executable=None, storages_basepath=None, storages=None,
                 storages_excludes=None, logger=None, indent=None):
        self.storages_basepath = storages_basepath or Path.cwd()
        self.executable = executable + " " if executable else ""
        self.logger = logger or NoOperationLogger()
        self.storages = storages or []
        self.storages_excludes = storages_excludes or []
        self.indent = indent

        self.apps = self.load(apps)

    def get_diskette_version(self):
        """
        Shortand to return diskette version.

        Useful with manifest building so it can be easily mocked from tests.

        Returns:
            string: The version string.
        """
        return versionning.get_package_version()["version"]

    def get_drain_exclusions(self, apps, drain_excluded=False):
        """
        Get all model labels that should be excluded from a Drain to respect drainage
        policy.

        Arguments:
            apps (list): List of ``ApplicationConfig`` or ``DrainApplicationConfig``
                objects.

        Keyword Arguments:
            drain_excluded (boolean): If True, the excluded models are also returned for
                application which allows it with their ``allow_drain`` option. If False
                the excluded model won't be included. Default is False.

        Returns:
            list: List of FQM labels.
        """
        labels = []

        for app in apps:
            # If drain accept exclusions, blindly follow the apps retentions
            if drain_excluded:
                labels.extend(app.retention)
            # If drain reject exclusions, ignores app policy and force exclusions
            else:
                labels.extend(
                    unduplicated_merge_lists(app.retention, app.excludes)
                )

        return labels

    def load(self, apps):
        """
        Load application objects from given definitions.

        Arguments:
            apps (list): List of dictionnaries where each one is an application.

        Returns:
            list: List of application objects built from given definitions.
        """
        objects = []
        drains = []

        # Check for duplicated name
        twices = list(get_duplicates([name for name, options in apps]))
        if twices:
            raise DumperError(
                "There was some duplicate names from applications: {}".format(
                    ", ".join(twices)
                )
            )

        # Build registry of application models
        objects = []
        for name, options in apps:
            if not options.get("is_drain"):
                # 'is_drain' is not meant to be passed as model argument
                options.pop("is_drain", None)
                # Append initialized app model
                objects.append(ApplicationConfig(name, **options))

        # Add drain models to registry
        drains = []
        for name, options in apps:
            if options.get("is_drain"):
                # Merge explicit drain exclusions with involved app models to
                # exclude
                options["excludes"] = unduplicated_merge_lists(
                    self.get_drain_exclusions(
                        objects,
                        drain_excluded=options.get("drain_excluded", False)
                    ),
                    options.get("excludes", []),
                )
                # 'is_drain' is not meant to be passed as model argument
                options.pop("is_drain", None)
                # Append initialized drain model
                drains.append(DrainApplicationConfig(name, **options))

        return objects + drains

    def dump_options(self):
        """
        Build a dictionnary of options for each application.

        By option we means dump options given to dumpdata.

        Returns:
            list: List of dictionnaries, each dictionnary is a payload of application
                options.
        """
        return [app.as_options() for app in self.apps]

    def payload(self):
        """
        Build a dictionnary of configuration payload for each application.

        Returns:
            list: List of dictionnaries, each dictionnary is a payload of application
                definition parameters.
        """
        return [app.as_config() for app in self.apps]

    def build_commands(self, destination=None, indent=None):
        """
        Build dumpdata command line for each application.

        Keyword Arguments:
            destination (string or Path): Destination file where to write dump if
                given. The file will be created by the dump command when executed, not
                during this method.
            indent (integer): Indentation level for dump data.

        Returns:
            list: List of tuples for processed applications, each tuple contains
                firstly application name then the built dump command.
        """
        return [
            (
                app.name,
                self.command(app, destination=destination, indent=indent)
            )
            for app in self.apps
        ]

    def dump_data(self, destination=None, indent=None, check=False):
        """
        Call dumpdata command to dump each application data.

        Keyword Arguments:
            destination (string or Path): Destination file where to write dump if
                given. The file will be created by the dump command when executed, not
                during this method.
            indent (integer): Indentation level for dump data.
            check (boolean): Perform operations writhout writing or querying anything.

        Returns:
            list: List of tuples for processed applications, each tuple contains
                firstly application name then the command output.
        """
        return [
            (
                app.name,
                self.call(app, destination=destination, indent=indent, check=check)
            )
            for app in self.apps
        ]

    def validate_applications(self):
        """
        Call validators from all enabled application model objects.

        Raises:
            ApplicationRegistryError: An error with all possible collected errors if
            there is any.
        """
        errors = {}

        # Collect all model errors
        for app in self.apps:
            try:
                app.validate()
            except ApplicationConfigError as e:
                errors[app.name] = str(e)

        # Raise a single exception containing all collected errors
        if errors:
            raise ApplicationRegistryError(error_messages=errors)

    def format_archive_filename(self, filename, with_data=False, with_storages=False):
        """
        Format archive filename depending features.

        Keyword Arguments:
            filename (string): Filename to use instead. It must end with ``.tar.gz``.
                Filename format should be like ``diskette{features}.tar.gz`` where
                features pattern can include either ``_data``, ``_storages`` or both
                depending enabled dump kinds.
            with_data (boolean): Enable dump of application datas.
            with_storages (boolean): Enable dump of media storages.

        Returns:
            string: Formatted filename with features.
        """
        filename_features = ""
        if with_data is True:
            filename_features += "_data"
        if with_storages is True:
            filename_features += "_storages"

        return filename.format(features=filename_features)

    def build_dump_manifest(self, destination, data_path, with_data=True,
                            with_storages=True):
        """
        Build dump JSON manifest.

        Example of built file (real build is not indented): ::

            {
                "version": "0.0.0",
                "creation": "2024-01-01T12:12:12",
                "datas": [
                    "data/djangocontribsites.json",
                    "data/djangocontribauth.json"
                ],
                "storages": [
                    "var/media"
                ]
            }

        .. Note::
            Involves relative path resolving so it implies that storage paths are
            proper children of given destination path (that is removed from lead of
            storage paths).

            So storage paths must all start with a starting portion of value from
            Dumper attribute ``storages_basepath``.

            As an example ``/foo/bar/storage`` would not be in a 'storages_basepath'
            ``/ping/`` (so it is invalid) but would be (and valid) in ``/foo`` or
            ``/foo/bar``.

        .. Note::
            Manifest preserve order of registered applications when writing data dump
            list so it safe for loading them.

        Arguments:
            destination (Path): Destination file where to write manifest.

        Keyword Arguments:
            with_data (boolean): Enable dump of application datas.
            with_storages (boolean): Enable dump of media storages.

        Returns:
            Path: Path to the written manifest file.
        """
        manifest_path = destination / self.MANIFEST_FILENAME
        data = {
            "version": self.get_diskette_version(),
            "creation": datetime.datetime.now().isoformat(timespec="seconds"),
            "datas": None,
            "storages": None,
        }

        # Build a list of expected data dump filenames from registered applications
        if with_data is True:
            data["datas"] = [
                str((data_path / app.filename).relative_to(destination))
                for app in self.apps
            ]

        # Build a list of expected storage dump directories from registered storages
        if with_storages is True:
            data["storages"] = [
                str(storage.relative_to(self.storages_basepath))
                for storage in self.storages
            ]

        # Write built manifest into destination path
        manifest_path.write_text(json.dumps(data))

        return manifest_path

    def validate(self):
        """
        Call all validators
        """
        self.validate_applications()
        self.validate_storages()

    def make_archive(self, destination, filename, with_data=True, with_storages=True,
                     with_storages_excludes=True, destination_chmod=None):
        """
        Dump data and storages then archive everything in an archive.

        .. Note::
            Arguments 'with_data' and 'with_storages' can not be both disabled, at
            least one must be enabled else it is assumed as an error.

        Arguments:
            destination (Path): Directory where to write archive file.

        Keyword Arguments:
            filename (string): Custom archive filename to use instead of the default
                one. Your custom filename must end with ``.tar.gz``. Default filename
                is ``diskette[_data][_storages].tar.gz`` (parts depend from options).
            with_data (boolean): Enable dump of application datas.
            with_storages (boolean): Enable dump of media storages.
            with_storages_excludes (boolean): Enable usage of excluding patterns when
                collecting storages files.
            destination_chmod (integer): File permission to apply on archive files and
                also on destination directory if it did not exists. Value must be in
                an octal notation, default is ``0o755``.

        Returns:
            Path: Path to the written archive file.
        """
        destination_chmod = (
            destination_chmod or settings.DISKETTE_DUMP_PERMISSIONS or 0o755
        )

        if not with_data and not with_storages:
            raise DumperError(
                "Arguments 'with_data' and 'with_storages' can not be both 'False'"
            )

        # Temporary directory where the manager will work
        destination_tmpdir = Path(tempfile.mkdtemp(prefix=self.TEMPDIR_PREFIX))

        # Build data dump destination path
        data_tmpdir = destination_tmpdir / "data"
        data_tmpdir.mkdir()

        # Dump data into temp directory
        if with_data is True:
            self.dump_data(destination=data_tmpdir, indent=self.indent)

        # Compute history/stats file
        manifest_path = self.build_dump_manifest(
            destination_tmpdir,
            data_tmpdir,
            with_data=with_data,
            with_storages=with_storages
        )

        # Build dump archive paths
        archive_filename = self.format_archive_filename(
            filename,
            with_data=with_data,
            with_storages=with_storages
        )
        archive_path = destination_tmpdir / archive_filename
        archive_destination = destination / archive_filename

        # Then add everything to the archive
        try:
            with tarfile.open(archive_path, "w:gz") as tar:
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
                        self.logger.debug("- {name} ({size})".format(
                            name=arcname,
                            size=filesizeformat(path.stat().st_size),
                        ))
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
            shutil.move(archive_path, archive_destination)
            archive_destination.chmod(destination_chmod)

        finally:
            # Always remove temporary working directory
            if destination_tmpdir.exists():
                shutil.rmtree(destination_tmpdir)

        return archive_destination

    def make_script(self, destination, with_data=True, with_storages=True,
                    with_storages_excludes=True):
        """
        Create shellscript command lines to dump data.

        Arguments:
            destination (Path): Directory where to write archive file.

        Keyword Arguments:
            with_data (boolean): Enable dump of application datas.
            with_storages (boolean): Enable dump of media storages.
            with_storages_excludes (boolean): Enable usage of excluding patterns when
                collecting storages files.

        Returns:
            string: All commands to dump data, each command on its line with a previous
                comment line with the dump name.
        """
        if not with_data and not with_storages:
            raise DumperError(
                "Arguments 'with_data' and 'with_storages' can not be both 'False'"
            )

        commandlines = []

        # Dump data into temp directory
        if with_data is True:
            commandlines += [
                "# {}\n{}".format(name, cmd)
                for name, cmd in self.build_commands(
                    destination=destination,
                    indent=self.indent
                )
            ]

        return "\n".join(commandlines)

    def check(self, destination, filename, with_data=True, with_storages=True,
              with_storages_excludes=True):
        """
        Check what would be done.

        Arguments:
            destination (Path): Directory where to write archive file.

        Keyword Arguments:
            filename (string): Custom archive filename to use instead of the default
                one. Your custom filename must end with ``.tar.gz``. Default filename
                is ``diskette[_data][_storages].tar.gz`` (parts depend from options).
            with_data (boolean): Enable dump of application datas.
            with_storages (boolean): Enable dump of media storages.
            with_storages_excludes (boolean): Enable usage of excluding patterns when
                collecting storages files.

        Returns:
            Path: Path to the written archive file.
        """
        if not with_data and not with_storages:
            raise DumperError(
                "Arguments 'with_data' and 'with_storages' can not be both 'False'"
            )

        # Dump data into temp directory
        if with_data is True:
            self.dump_data(destination=destination, indent=self.indent, check=True)

        if with_storages is True:
            self.logger.info("- Scanning storages to archive")
            files_length = 0
            files_total = 0
            for path, arcname in self.iter_storages_files(
                allow_excludes=with_storages_excludes
            ):
                files_length += 1
                size = path.stat().st_size
                files_total += size
                self.logger.debug("- {name} ({size})".format(
                    name=arcname,
                    size=filesizeformat(size),
                ))

            if not files_length:
                self.logger.warning("  - No file has been found in any storage")
            else:
                msg = "- {length} file(s) would be collected for a total of {size}"
                self.logger.info(
                    msg.format(
                        length=files_length,
                        size=filesizeformat(files_total),
                    )
                )

            archive_filename = self.format_archive_filename(
                filename,
                with_data=with_data,
                with_storages=with_storages
            )

            return destination / archive_filename
