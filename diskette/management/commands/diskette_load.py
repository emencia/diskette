from pathlib import Path

from django.core.management.base import BaseCommand

from ...core.handlers import LoadCommandHandler
from ...utils.loggers import DjangoCommandOutput


class Command(BaseCommand, LoadCommandHandler):
    """
    Diskette load.
    """
    help = (
        "Restore application datas and storage files from a Diskette archive file "
        "(TAR GZ)."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "archive",
            default=None,
            help=(
                "Archive file path to restore its content."
            )
        )
        parser.add_argument(
            "--storages-basepath",
            type=Path,
            default=None,
            help="Directory path where to restore storage contents.",
        )
        parser.add_argument(
            "--no-data",
            action="store_true",
            help="Disable application data restoration.",
        )
        parser.add_argument(
            "--no-storages",
            action="store_true",
            help="Disable storages restoration.",
        )
        parser.add_argument(
            "--keep",
            action="store_true",
            help="Don't automatically remove archive when finished.",
        )

    def handle(self, *args, **options):
        self.logger = DjangoCommandOutput(command=self, verbosity=options["verbosity"])

        self.load(
            options["archive"],
            storages_basepath=options["storages_basepath"],
            no_data=options["no_data"],
            no_storages=options["no_storages"],
            keep=options["keep"],
        )
