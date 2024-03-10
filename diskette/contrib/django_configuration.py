from ..settings import (
    DISKETTE_APPS,
    DISKETTE_STORAGES,
    DISKETTE_STORAGES_EXCLUDES,
    DISKETTE_DUMP_PATH,
    DISKETTE_DUMP_FILENAME,
    DISKETTE_LOAD_STORAGES_PATH,
)


class DisketteDefaultSettings:
    """
    Default Diskette settings class to use with a "django-configuration" class.

    Example:

        You could use it like so: ::

            from configurations import Configuration
            from diskette.contrib.django_configuration import DisketteDefaultSettings

            class Dev(DisketteDefaultSettings, Configuration):
                DEBUG = True

                DISKETTE_DUMP_FILENAME = "foo.tar.gz"

        This will override only the setting ``DISKETTE_DUMP_FILENAME``, all other
        Diskette settings will have the default values from ``diskette.settings``.
    """

    DISKETTE_APPS = DISKETTE_APPS

    DISKETTE_STORAGES = DISKETTE_STORAGES

    DISKETTE_STORAGES_EXCLUDES = DISKETTE_STORAGES_EXCLUDES

    DISKETTE_DUMP_PATH = DISKETTE_DUMP_PATH

    DISKETTE_DUMP_FILENAME = DISKETTE_DUMP_FILENAME

    DISKETTE_LOAD_STORAGES_PATH = DISKETTE_LOAD_STORAGES_PATH