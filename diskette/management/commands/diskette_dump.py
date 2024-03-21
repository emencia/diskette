from pathlib import Path

from django.core.management.base import BaseCommand

from ...core.handlers import DumpCommandHandler
from ...utils.loggers import DjangoCommandOutput
from ...exceptions import ApplicationRegistryError


class Command(BaseCommand, DumpCommandHandler):
    """
    Diskette dump.
    """
    help = (
        "Dump configured application data and media files into an archive (TAR GZ)."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--destination",
            type=Path,
            metavar="PATH",
            default=None,
            help=(
                "Directory path where to write the dump archive. If given path does "
                "not exists it will be created. Default to current working directory."
            )
        )
        parser.add_argument(
            "--filename",
            type=str,
            metavar="FILENAME",
            default=None,
            help=(
                "Custom archive filename to use for this dump. This is only the "
                "filename, don't include directory path here. Your filename must ends "
                "with 'tar.gz'."
            )
        )
        parser.add_argument(
            "--appconf",
            type=Path,
            metavar="PATH",
            default=None,
            help=(
                "Path to a JSON file with application configurations for data dump. "
                "This will overwrite application configurations settings."
            ),
        )
        parser.add_argument(
            "--storage",
            type=Path,
            metavar="PATH",
            action="append",
            default=[],
            help=(
                "This is a cumulative argument. Using this argument will overwrite "
                "storages settings."
            )
        )
        parser.add_argument(
            "--storages-basepath",
            type=Path,
            default=None,
            help="Custom basepath to resolve storage files paths.",
        )
        parser.add_argument(
            "--storages-exclude",
            type=str,
            metavar="PATTERN",
            action="append",
            default=[],
            help=(
                "This is a cumulative argument. Using this argument will overwrite "
                "storage excludes settings."
            )
        )
        parser.add_argument(
            "--indent",
            type=int,
            help="Specifies the indent level to use when pretty-printing output.",
        )
        parser.add_argument(
            "--no-data",
            action="store_true",
            help="Disable application data dumps.",
        )
        parser.add_argument(
            "--no-storages",
            action="store_true",
            help="Disable storages dump.",
        )
        parser.add_argument(
            "--no-storages-excludes",
            action="store_true",
            help="Disable usage of storage excluding patterns.",
        )
        parser.add_argument(
            "--no-archive",
            action="store_true",
            help="Output command lines to perform dumps instead of making an archive.",
        )

    def handle(self, *args, **options):
        self.logger = DjangoCommandOutput(command=self, verbosity=options["verbosity"])

        try:
            if not options["no_archive"]:
                self.dump(
                    options["destination"],
                    archive_filename=options["filename"],
                    application_configurations=options["appconf"],
                    storages=options["storage"],
                    storages_basepath=options["storages_basepath"],
                    storages_excludes=options["storages_exclude"],
                    no_data=options["no_data"],
                    no_storages=options["no_storages"],
                    no_storages_excludes=options["no_storages_excludes"],
                    indent=options["indent"],
                )
            else:
                """
                TODO:
                    * This has no test coverage yet;
                    * It lacks of storage copy commands;
                    * dumpdata command currently output to temporary directory
                      instead of proper data directory;
                """
                self.stdout.write(
                    self.script(
                        application_configurations=options["appconf"],
                        storages=options["storage"],
                        storages_basepath=options["storages_basepath"],
                        storages_excludes=options["storages_exclude"],
                        no_data=options["no_data"],
                        no_storages=options["no_storages"],
                        no_storages_excludes=options["no_storages_excludes"],
                        indent=options["indent"],
                    )
                )
        except ApplicationRegistryError as excinfo:
            # Manage specific registry error that may include a detail
            self.logger.error(excinfo)
            for msg in excinfo.get_payload_details():
                self.logger.error(msg)
            self.logger.critical("Aborted operation.")
