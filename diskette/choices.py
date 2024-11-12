from django.utils.translation import gettext_lazy as _


STATUS_CREATED = 0
"""
Created status numeric value
"""

STATUS_PENDING = 10
"""
Pending status numeric value
"""

STATUS_FAILED = 20
"""
Failure status numeric value
"""

STATUS_PROCESSED = 30
"""
Processed status numeric value
"""

STATUS_CHOICES = (
    (STATUS_CREATED, _("created")),
    (STATUS_PENDING, _("pending")),
    (STATUS_FAILED, _("failed")),
    (STATUS_PROCESSED, _("processed")),
)
"""
Status choice list
"""


def get_status_choices():
    """
    Callable to get choice list.
    """
    return STATUS_CHOICES


def get_status_default():
    """
    Callable to get default choice value.
    """
    return STATUS_CREATED
