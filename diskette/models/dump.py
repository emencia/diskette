from pathlib import Path

from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.utils import timezone

from ..choices import get_status_choices, get_status_default


class DumpFile(models.Model):
    """
    Created dump file history object.

    We still keep deprecated dump for history but their files won't be available, in
    fact the same filename could be available but it would be overwritten by a new
    dump.

    Attributes:
        created (models.DateTimeField): Required creation datetime, automatically
            filled.
        processed (models.DateTimeField): Datetime for when the related dump processed
            and further related object updates have ended.
        status (models.SmallIntegerField): Required article status.
        with_data (models.BooleanField): Option to enable data save in dump.
        with_storage (models.BooleanField): Option to enable storage medias save in
            dump.
        deprecated (models.BooleanField): Option to mark a dump as deprecated after a
            new one with the same options has been created.
        path (models.CharField): Required unique absolute directory path.
        checksum (models.CharField): Required unique checksum string.
        size (models.BigIntegerField): Dump file size integer.
        logs (models.TextField): Stored logs for a sucessful process dump.
    """
    created = models.DateTimeField(
        _("creation date"),
        db_index=True,
        default=timezone.now,
    )
    processed = models.DateTimeField(
        _("processed date"),
        db_index=True,
        blank=True,
        null=True,
        default=None,
    )
    status = models.SmallIntegerField(
        _("status"),
        db_index=True,
        choices=get_status_choices(),
        default=get_status_default(),
        help_text=_(
            "Process status."
        ),
    )
    with_data = models.BooleanField(
        verbose_name=_("with data"),
        default=True,
        blank=True,
        help_text=_(
            "This dump contains data."
        ),
    )
    with_storage = models.BooleanField(
        verbose_name=_("with storage"),
        default=True,
        blank=True,
        help_text=_(
            "This dump contains storage medias."
        ),
    )
    deprecated = models.BooleanField(
        verbose_name=_("deprecated"),
        default=False,
        blank=True,
        db_index=True,
        help_text=_(
            "A deprecated dump can not be downloaded anymore. WARNING: Deprecation "
            "can not be reversed."
        ),
    )
    path = models.TextField(
        _("path"),
        blank=False,
        default="",
    )
    checksum = models.CharField(
        _("checksum"),
        blank=True,
        max_length=128,
        default="",
        help_text=_(
            "A blake2 hash for dump file checksum."
        ),
    )
    size = models.BigIntegerField(
        _("archive size"),
        blank=True,
        default=0,
        validators=[MinValueValidator(0)],
    )
    logs = models.TextField(
        _("process logs"),
        blank=True,
        default="",
    )

    class Meta:
        verbose_name = _("Dump")
        verbose_name_plural = _("Dumps")
        ordering = [
            "-created",
        ]

    def __str__(self):
        return self.created.isoformat(timespec="seconds")

    def purge_file(self, commit=True):
        """
        Remove path file if it exists then prefix its path with a mark "removed:/"
        """
        filepath = Path(self.path)

        filepath.unlink(missing_ok=True)
        self.path = "removed:/" + self.path

        if commit:
            self.save()

    @classmethod
    def purge_deprecated_dumps(cls):
        """
        Remove dump file from all deprecated dumps that were not already purged.

        This will alter the dump path to prefix it with a mark ``removed:/`` that is
        used to recognize purged dumps.
        """
        purge_queryset = cls.objects.filter(deprecated=True).exclude(
            path__startswith="removed:/"
        )
        for deprecated_dumps in purge_queryset:
            deprecated_dumps.purge_file()

    def delete(self, *args, **kwargs):
        """
        Delete dump file once its object has been deleted.
        """
        holded_filepath = self.path

        super().delete(*args, **kwargs)

        self.purge_file(commit=False)
