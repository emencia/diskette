import logging
from io import StringIO
from pathlib import Path

from django.conf import settings
from django.utils import timezone

from ..choices import STATUS_CREATED, STATUS_PROCESSED
from ..core.handlers import DumpCommandHandler
from ..models import DumpFile
from ..utils import hashs


def post_dump_save_process(obj):
    """
    Launch dump process and maintain dump object status.

    .. NOTE:
        This may help to implement custom post processing with something like django-q
        or another queue library.

        Also this could be divided in two functions, one to save pending status then
        launching process and another alike a callback to fill infos from archive and
        finalize to status processed.
    """
    # Process dump can only happens for a new created object
    if not obj.deprecated and obj.status == STATUS_CREATED:
        archive_destination = settings.DISKETTE_DUMP_PATH or Path.cwd()
        # Get dump handler with a custom logger to catch process logs to store
        dumper = DumpCommandHandler()
        dummystream = StringIO()
        handler = logging.StreamHandler(dummystream)
        dumper.logger = logging.getLogger("diskette_dump_process")
        dumper.logger.setLevel(logging.DEBUG)
        dumper.logger.addHandler(handler)

        # Fix end processing datetime
        dump_processed = timezone.now()
        # Build filename from creation datetime
        isodate = obj.created.isoformat().replace(".", "").replace(":", "")
        archive_filename = "diskette_{}.tar.gz".format(isodate.split("+")[0])

        # Build dump
        archive_file = dumper.dump(
            archive_destination=archive_destination,
            archive_filename=archive_filename,
            application_configurations=settings.DISKETTE_APPS,
            storages=settings.DISKETTE_STORAGES,
            storages_excludes=settings.DISKETTE_STORAGES_EXCLUDES,
            no_data=not obj.with_data,
            no_checksum=False,
            no_storages=not obj.with_storage,
            no_storages_excludes=False,
            check=False,
        )

        # Get the created dump checksum
        archive_checksum = hashs.file_checksum(archive_file)

        # Update object to fill data related to processed dump
        obj.path = str(archive_file.relative_to(archive_destination))
        obj.size = archive_file.stat().st_size
        obj.processed = dump_processed
        obj.checksum = archive_checksum
        obj.status = STATUS_PROCESSED
        obj.logs = dummystream.getvalue()
        obj.save(update_fields=[
            "path",
            "size",
            "status",
            "processed",
            "checksum",
            "logs",
        ])

        # Purge handler from the process logger
        dumper.logger.removeHandler(handler)

        # Purge all deprecated dumps from their file
        if settings.DISKETTE_DUMP_AUTO_PURGE:
            DumpFile.purge_deprecated_dumps()

    return obj
