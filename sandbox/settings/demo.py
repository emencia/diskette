"""
Django settings for demonstration

Intended to be used with ``make run``.
"""
from sandbox.settings.base import *  # noqa: F403

DEBUG = True

TEMPLATES[0]['OPTIONS']['debug'] = DEBUG  # noqa: F405

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": VAR_PATH / "db" / "db.sqlite3",  # noqa: F405
    }
}

DISKETTE_APPS = [
    [
        "django.contrib.sites", {
            "comments": "django.contrib.sites",
            "natural_foreign": True,
            "models": "sites"
        }
    ],
    [
        "django.contrib.auth", {
            "comments": "django.contrib.auth: user and groups, no perms",
            "natural_foreign": True,
            "models": ["auth.group","auth.user"]
        }
    ]
]

DISKETTE_STORAGES = [MEDIA_ROOT]
DISKETTE_STORAGES_EXCLUDES = ["cache/*"]

# Import local settings if any
try:
    from .local import *  # noqa: F401,F403
except ImportError:
    pass
