import json
from pathlib import Path

from django.conf import settings
from django.template.defaultfilters import filesizeformat

from ...utils import hashs
from ..dumper import Dumper


class DumpCommandHandler:
    """
    Abstraction layer between Dumper and the management command, it holds getters
    to get and validate values for manager options and provide a shortand to
    dump or load contents with options.

    This relies on ``logger`` attribute that is not provided here. The logger object
    should be one of compatible classes from ``diskette.utils.loggers``.
    """
    def get_archive_destination(self, path=None):
        """
        Either get the archive destination path from given argument if given else from
        ``settings.DISKETTE_DUMP_PATH``.

        Arguments:
            path (Path): Path object to a directory.

        Returns:
            Path: Discovered path.
        """
        path = path or settings.DISKETTE_DUMP_PATH

        if not path:
            self.logger.critical("Destination path can not be an empty value")

        self.logger.debug(
            "- Tarball will be written into: {}".format(path)
        )

        return path

    def get_archive_filename(self, filename=None):
        """
        Either get the archive destination filename from given argument if given else
        from ``settings.DISKETTE_DUMP_FILENAME``.

        Keyword Arguments:
            filename (string): Filename.

        Returns:
            Path: Discovered filename.
        """
        filename = filename or settings.DISKETTE_DUMP_FILENAME

        if not filename:
            self.logger.critical("Destination filename can not be an empty value")

        self.logger.debug(
            "- Tarball filename pattern: {}".format(filename)
        )

        return filename

    def get_application_configurations(self, appconfs=None, no_data=False):
        """
        Either get the application configurations from ``appconfs`` value if not empty,
        else from ``settings.DISKETTE_APPS``.

        Keyword Arguments:
            appconfs (string or list or Path): Either:

                * A list which includes application configurations;
                * A string which holds valid JSON;
                * A Path object to a JSON file to open to get application
                  configurations;

                If None or any empty value, the setting will be used.
            no_data (boolean): Value of argument to explicitely disable data dump.

        Returns:
            tuple: A boolean value that is True if dump is enabled and a list of
                application configuration has been discovered.
        """
        if no_data is True:
            self.logger.debug("- Data dump is disabled")
            return False, []

        apps = []
        if isinstance(appconfs, Path):
            apps = json.loads(appconfs.read_text())
        elif isinstance(appconfs, str) and appconfs:
            apps = json.loads(appconfs)
        elif isinstance(appconfs, list):
            apps = appconfs

        apps = apps or settings.DISKETTE_APPS

        if apps:
            self.logger.debug("- Data dump enabled for application:")
            for i, item in enumerate(apps, start=1):
                msg = "  ├── {}" if i < len(apps) else "  └── {}"
                self.logger.debug(msg.format(item[0]))
        else:
            self.logger.debug("- No application defined, data dump is disabled.")
            return False, []

        return True, apps

    def get_storage_paths(self, paths=None, no_storages=False):
        """
        Returns given storage paths from args if any else use
        ``settings.DISKETTE_STORAGES``.

        Keyword Arguments:
            paths (list): List of Path object for storage paths to use instead of the
                ones from settings. If empty, the paths defined in settings are used.
            no_storages (boolean): Value of argument to explicitely disable storage
                dump.

        Returns:
            tuple: A boolean value that is True if dump is enabled and a list of
                storage Path objects.
        """
        if no_storages is True:
            self.logger.debug("- Storage dump is disabled")
            return False, []

        storages = paths or settings.DISKETTE_STORAGES

        if storages:
            self.logger.debug("- Storage dump enabled for:")
            for i, item in enumerate(storages, start=1):
                msg = "  ├── {}" if i < len(storages) else "  └── {}"
                self.logger.debug(msg.format(item))
        else:
            self.logger.debug("- No storage defined, storage dump is disabled.")
            return False, []

        return True, storages

    def get_storage_excludes(self, patterns=None, no_patterns=False):
        """
        Get exclude patterns either from args if given, else use the default ones from
        ``settings.DISKETTE_STORAGES_EXCLUDES``.

        Arguments:
            patterns (list): List of patterns to use instead of the ones from settings.
                If empty, the paths defined in settings are used.
            no_patterns (boolean): Value of argument to explicitely disable storage
                excluding patterns usage.

        Returns:
            tuple: A boolean value that is True if pattern usage is enabled and a list
                of patterns to use if any.
        """
        if no_patterns is True:
            self.logger.debug("- Storage exclude patterns are disabled")
            return False, []

        patterns = patterns or settings.DISKETTE_STORAGES_EXCLUDES

        if patterns:
            self.logger.debug("- Storage exclude patterns enabled:")
            for i, item in enumerate(patterns, start=1):
                msg = "  ├── {}" if i < len(patterns) else "  └── {}"
                self.logger.debug(msg.format(item))
        else:
            self.logger.debug("- No storage exclude patterns defined.")
            return False, []

        return True, patterns

    def script(self, application_configurations=None, storages=None,
               storages_basepath=None, storages_excludes=None, no_data=False,
               no_storages=False, no_storages_excludes=False, indent=None):
        """
        Create shellscript command lines to dump data and storages.

        .. Note::
            This does not involve argument validation methods like
            ``get_archive_destination`` and others here.

        Keyword Arguments:
            filename (string): Custom archive filename to use instead of the default
                one. Your custom filename must end with ``.tar.gz``. Default filename
                is ``diskette[_data][_storages].tar.gz`` (parts depend from options).
            application_configurations (string or list or Path): Either:

                * A list which includes application configurations;
                * A string which holds valid JSON;
                * A Path object to a JSON file to open to get application
                  configurations;

                If None or any empty value, the setting will be used.
            storages (list): A list of storage Path objects.
            storages_basepath (Path): Basepath for reference in some path resolution.
                Currently used by storage dump to make relative path for storage files.
                On default this is based on current working directory. If given, the
                storage paths must be in the same leaf else this will be an error.
            storages_excludes (list): A list of patterns to exclude storage files from
                dump.
            no_data (boolean): Disable dump of application datas.
            no_storages (boolean): Disable dump of media storages.
            no_storages_excludes (boolean): Disable usage of excluding patterns when
                collecting storages files.
            indent (integer): Indentation level in data dumps. If not given, dumps won't
                be indented.

        Returns:
            string: All commands to dump data, each command on its line with a previous
                comment line with the dump name.
        """
        self.logger.info("=== Starting script ===")

        with_data, application_configurations = self.get_application_configurations(
            appconfs=application_configurations,
            no_data=no_data
        )

        with_storages, storages = self.get_storage_paths(storages, no_storages)
        with_storages_excludes = None
        if with_storages:
            with_storages_excludes, storages_excludes = self.get_storage_excludes(
                storages_excludes,
                no_patterns=no_storages_excludes,
            )
        else:
            storages_excludes = []

        if not with_data and not with_storages:
            self.logger.critical(
                "Data and storages dumps can not be both disabled. At least one dump "
                "type must be enabled."
            )

        dumper = Dumper(
            application_configurations,
            logger=self.logger,
            storages_basepath=storages_basepath,
            storages=storages,
            storages_excludes=storages_excludes,
            indent=indent,
        )

        # Validate configurations
        dumper.validate()

        commandlines = dumper.make_script(
            with_data=with_data,
            with_storages=with_storages,
            with_storages_excludes=with_storages_excludes,
        )

        return commandlines

    def dump(self, archive_destination, archive_filename=None,
             application_configurations=None, storages=None, storages_basepath=None,
             storages_excludes=None, no_data=False, no_checksum=False,
             no_storages=False, no_storages_excludes=False, indent=None):
        """
        Proceed to dump datas and storages collection into an archive.

        .. Note::
            This does not involve argument validation methods like
            ``get_archive_destination`` and others here.

        Arguments:
            archive_destination (Path):

        Keyword Arguments:
            archive_filename (string): Custom archive filename to use instead of the
                default one. Your custom filename must end with ``.tar.gz``. Default
                filename is ``diskette[_data][_storages].tar.gz`` (parts depend from
                options).
            application_configurations (string or list or Path): Either:

                * A list which includes application configurations;
                * A string which holds valid JSON;
                * A Path object to a JSON file to open to get application
                  configurations;

                If None or any empty value, the setting will be used.
            storages (list): A list of storage Path objects.
            storages_basepath (Path): Basepath for reference in some path resolution.
                Currently used by storage dump to make relative path for storage files.
                On default this is based on current working directory. If given, the
                storage paths must be in the same leaf else this will be an error.
            storages_excludes (list): A list of patterns to exclude storage files from
                dump.
            no_data (boolean): Disable dump of application datas.
            no_checksum (boolean): Disable archive checksum.
            no_storages (boolean): Disable dump of media storages.
            no_storages_excludes (boolean): Disable usage of excluding patterns when
                collecting storages files.
            indent (integer): Indentation level in data dumps. If not given, dumps won't
                be indented.

        Returns:
            Path: Path to the written archive file.
        """
        self.logger.info("=== Starting dump ===")

        archive_destination = self.get_archive_destination(archive_destination)
        archive_filename = self.get_archive_filename(archive_filename)

        with_data, application_configurations = self.get_application_configurations(
            appconfs=application_configurations,
            no_data=no_data
        )

        with_storages, storages = self.get_storage_paths(storages, no_storages)
        with_storages_excludes = None
        if with_storages:
            with_storages_excludes, storages_excludes = self.get_storage_excludes(
                storages_excludes,
                no_patterns=no_storages_excludes,
            )
        else:
            storages_excludes = []

        if not with_data and not with_storages:
            self.logger.critical(
                "Data and storages dumps can not be both disabled. At least one dump "
                "type must be enabled."
            )

        dumper = Dumper(
            application_configurations,
            logger=self.logger,
            storages_basepath=storages_basepath,
            storages=storages,
            storages_excludes=storages_excludes,
            indent=indent,
        )

        # Validate configuration
        dumper.validate()

        archive_path = dumper.make_archive(
            archive_destination,
            archive_filename,
            with_data=with_data,
            with_storages=with_storages,
            with_storages_excludes=with_storages_excludes,
        )

        self.logger.info(
            "Dump archive was created at: {path} ({size})".format(
                path=archive_path,
                size=filesizeformat(archive_path.stat().st_size),
            )
        )

        if not no_checksum:
            self.logger.info(
                "Checksum: {}".format(hashs.file_checksum(archive_path))
            )

        return archive_path
