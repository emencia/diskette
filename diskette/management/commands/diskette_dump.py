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
            "--no-checksum",
            action="store_true",
            help=(
                "Disable archive checksum. Default behavior is to always compute a "
                "checksum of created archive and output it."
            ),
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
            help=(
                "Output command lines to perform data dumps instead of making an "
                "archive. This does not care about storages, checksum, etc.. Note than"
                "those command lines will start directly with the command name. You "
                "will need to prefix them your proper path to 'django-admin' or "
                "'manage.py'."
            ),
        )

    def handle(self, *args, **options):
        self.logger = DjangoCommandOutput(command=self, verbosity=options["verbosity"])

        try:
            if not options["no_archive"]:
                self.dump(
                    archive_destination=options["destination"],
                    archive_filename=options["filename"],
                    application_configurations=options["appconf"],
                    storages=options["storage"],
                    storages_basepath=options["storages_basepath"],
                    storages_excludes=options["storages_exclude"],
                    no_data=options["no_data"],
                    no_checksum=options["no_checksum"],
                    no_storages=options["no_storages"],
                    no_storages_excludes=options["no_storages_excludes"],
                    indent=options["indent"],
                )
            else:
                self.stdout.write(
                    self.script(
                        archive_destination=options["destination"],
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
