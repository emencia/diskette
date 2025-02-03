from io import StringIO
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from ...exceptions import ApplicationRegistryError
from ...choices import STATUS_PROCESSED
from ...core.handlers import DumpCommandHandler
from ...models import DumpFile
from ...utils import hashs
from ...utils.loggers import DjangoCommandOutput


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
        parser.add_argument(
            "--check",
            action="store_true",
            help=(
                "Don't make archive or write anything on filesystem. Only validate "
                "configuration and output informations about dump. You should use "
                "this with option '-v 3' to get the whole informations."
            ),
        )
        parser.add_argument(
            "--save",
            action="store_true",
            help=(
                "Save a Dump object from created dump. This is incompatible with "
                "options '--check', '--no-archive' and with disabled admin."
            ),
        )

    def handle(self, *args, **options):
        with StringIO() as msg_buffer:
            self.logger = DjangoCommandOutput(
                command=self,
                verbosity=options["verbosity"],
                msg_buffer=msg_buffer,
            )

            if options["save"]:
                if (
                    options["check"] or
                    options["no_archive"] or
                    not settings.DISKETTE_ADMIN_ENABLED
                ):
                    self.logger.critical(
                        "The option '--save' is incompatible with options '--check', "
                        "'--no-archive' and disabled admin from setting "
                        "'DISKETTE_ADMIN_ENABLED'."
                    )

            try:
                if not options["no_archive"]:
                    archive_file = self.dump(
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
                        check=options["check"],
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
            else:
                if options["save"]:
                    # Create new dump object with created archive
                    destination = self.get_archive_destination(options["destination"])
                    dump = DumpFile(
                        with_data=not options["no_data"],
                        with_storage=not options["no_storages"],
                        deprecated=False,
                        path=str(archive_file.relative_to(destination)),
                        size=archive_file.stat().st_size,
                        checksum=hashs.file_checksum(archive_file),
                        status=STATUS_PROCESSED,
                        logs=self.logger.msg_buffer.getvalue(),
                    )
                    dump.processed = dump.created
                    dump.save()

                    # Deprecated previous identical dump(s)
                    DumpFile.objects.filter(
                        deprecated=False,
                        with_data=not options["no_data"],
                        with_storage=not options["no_storages"],
                    ).exclude(pk=dump.id).update(deprecated=True)

                    # Purge all deprecated dumps from their file
                    if settings.DISKETTE_DUMP_AUTO_PURGE:
                        DumpFile.purge_deprecated_dumps()
