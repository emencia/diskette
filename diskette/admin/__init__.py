from django.conf import settings

if settings.DISKETTE_ADMIN_ENABLED:

    from .dump import DumpFileAdmin
    from .key import APIkeyAdmin

    __all__ = [
        "APIkeyAdmin",
        "DumpFileAdmin",
    ]
