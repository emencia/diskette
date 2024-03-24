import logging
import shutil

import pytest

from django.apps import apps
from django.contrib.sites.models import Site

from diskette.core.handlers import LoadCommandHandler
from diskette.exceptions import DisketteError
from diskette.utils.loggers import LoggingOutput


@pytest.mark.parametrize("setting, arg, expected", [
    ("foo", None, "foo"),
    ("foo", "bar", "bar"),
    (None, "bar", "bar"),
])
def test_storages_basepath_valid(settings, setting, arg, expected):
    """
    Command properly discover the destination to use
    """
    commander = LoadCommandHandler()
    commander.logger = LoggingOutput()

    settings.DISKETTE_LOAD_STORAGES_PATH = setting
    assert commander.get_storages_basepath(arg) == expected


def test_storages_basepath_invalid(settings):
    """
    Command should raise an error when resolved value for archive destination is empty.
    """
    commander = LoadCommandHandler()
    commander.logger = LoggingOutput()

    settings.DISKETTE_LOAD_STORAGES_PATH = None
    with pytest.raises(DisketteError) as excinfo:
        commander.get_storages_basepath("")

    assert str(excinfo.value) == "Storages destination path can not be an empty value"


def test_load(caplog, settings, db, mocked_checksum, tests_settings, tmp_path):
    """
    Load method with the right arguments should correctly proceed to restore archive
    contents and output some logs.
    """
    caplog.set_level(logging.DEBUG)

    archive_name = "basic_data_storages.tar.gz"
    archive_path = tmp_path / archive_name
    shutil.copy(
        tests_settings.fixtures_path / "archive_samples" / archive_name,
        archive_path
    )

    commander = LoadCommandHandler()
    commander.logger = LoggingOutput()

    stats = commander.load(
        archive_path,
        tmp_path,
        no_data=False,
        no_storages=False,
    )

    # Archive has been removed once extracted
    assert archive_path.exists() is False

    # Query Site and User to check expected data from dumps
    user_app, user_model = settings.AUTH_USER_MODEL.split(".")
    User = apps.get_registered_model(user_app, user_model)
    assert User.objects.count() == 3
    assert Site.objects.count() == 2

    # Every storages should be present in destination and not empty
    for source, stored in stats["storages"]:
        assert stored.exists() is True
        assert len(list(stored.iterdir())) > 0

    # Flatten logging messages
    logs = [
        name + ":" + str(lv) + ":" + msg
        for name, lv, msg in caplog.record_tuples
    ]

    assert logs == [
        "diskette:20:=== Starting restoration ===",
        "diskette:10:- Storages contents will be restored into: {}".format(tmp_path),
        "diskette:10:Archive checksum: dummy-checksum",
        (
            "diskette:10:Creating storage parent directory: {}/storage_samples".format(
                tmp_path
            )
        ),
        "diskette:20:Restoring storage directory (7.2 KB): storage_samples/storage-1",
        "diskette:20:Restoring storage directory (9.6 KB): storage_samples/storage-2",
        "diskette:20:Loading data from dump 'django-auth.json' (959 bytes)",
        "diskette:10:Installed 3 object(s) from 1 fixture(s)",
        "diskette:20:Loading data from dump 'django-site.json' (194 bytes)",
        "diskette:10:Installed 2 object(s) from 1 fixture(s)"
    ]
