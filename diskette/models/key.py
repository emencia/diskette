import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class APIkey(models.Model):
    """
    API key object.

    Only an unique APIkey will be available at the same time and all others will
    be deprecated. We still keep deprecated keys for history. Obviously it should not
    be editable in any way. In fact nothing should be editable, this should just be a
    "fully fill an object automatically on creation" and that's all.

    Attributes:
        created (models.DateTimeField): Required creation datetime, automatically
            filled.
        key (models.CharField): Required unique key string.
        deprecated (models.BooleanField): Option to mark a key as deprecated after a
            new one has been created with the same options.
    """
    created = models.DateTimeField(
        _("creation date"),
        db_index=True,
        default=timezone.now,
    )
    key = models.UUIDField(
        _("public key"),
        default=uuid.uuid4,
        editable=False,
        unique=True,
        help_text=_(
            "Public key to use in requests to Diskette API."
        ),
    )
    deprecated = models.BooleanField(
        verbose_name=_("deprecated"),
        default=False,
        blank=True,
        db_index=True,
        help_text=_(
            "Depreciated keys are not available anymore for usage but are keeped for "
            "history. WARNING: Deprecation can not be reversed."
        ),
    )

    class Meta:
        verbose_name = _("API key")
        verbose_name_plural = _("API keys")
        ordering = [
            "-created",
        ]

    def __str__(self):
        return self.created.isoformat(timespec="seconds")
