import logging
import shutil
from pathlib import Path

import pytest

from django.apps import apps
from django.contrib.sites.models import Site

from diskette.core.handlers import LoadCommandHandler
from diskette.utils.loggers import LoggingOutput


@pytest.mark.parametrize("setting, arg, expected", [
    ("foo", None, "foo"),
    ("foo", "bar", "bar"),
    (None, "bar", "bar"),
    (None, None, Path.cwd()),
])
def test_storages_basepath_valid(settings, setting, arg, expected):
    """
    Command properly discover the destination to use
    """
    handler = LoadCommandHandler()
    handler.logger = LoggingOutput()

    settings.DISKETTE_LOAD_STORAGES_PATH = setting
    assert handler.get_storages_basepath(arg) == expected


@pytest.mark.parametrize("options, expected", [
    (
        {
            "no_data": False,
            "no_storages": False,
            "keep": True,
        },
        [
            "diskette:20:=== Starting restoration ===",
            "diskette:10:diskette==0.0.0-test",
            "diskette:10:- Storages contents will be restored into: {tmp_path}",
            "diskette:10:Archive checksum: dummy-checksum",
            "diskette:10:Creating storage parent directory: {tmp_path}/storage_samples",
            (
                "diskette:20:Restoring storage directory (7.2 KB): storage_samples/"
                "storage-1"
            ),
            (
                "diskette:20:Restoring storage directory (9.6 KB): storage_samples/"
                "storage-2"
            ),
            "diskette:20:Loading data from dump 'django-auth.json' (959 bytes)",
            "diskette:10:Installed 3 object(s) from 1 fixture(s)",
            "diskette:20:Loading data from dump 'django-site.json' (194 bytes)",
            "diskette:10:Installed 2 object(s) from 1 fixture(s)"
        ]
    ),
    (
        {
            "no_data": False,
            "no_storages": False,
            "checksum": False,
        },
        [
            "diskette:20:=== Starting restoration ===",
            "diskette:10:diskette==0.0.0-test",
            "diskette:10:- Storages contents will be restored into: {tmp_path}",
            "diskette:10:Creating storage parent directory: {tmp_path}/storage_samples",
            (
                "diskette:20:Restoring storage directory (7.2 KB): storage_samples/"
                "storage-1"
            ),
            (
                "diskette:20:Restoring storage directory (9.6 KB): storage_samples/"
                "storage-2"
            ),
            "diskette:20:Loading data from dump 'django-auth.json' (959 bytes)",
            "diskette:10:Installed 3 object(s) from 1 fixture(s)",
            "diskette:20:Loading data from dump 'django-site.json' (194 bytes)",
            "diskette:10:Installed 2 object(s) from 1 fixture(s)"
        ]
    ),
    (
        {
            "no_data": False,
            "no_storages": True,
        },
        [
            "diskette:20:=== Starting restoration ===",
            "diskette:10:diskette==0.0.0-test",
            "diskette:10:- Storages contents will be restored into: {tmp_path}",
            "diskette:10:Archive checksum: dummy-checksum",
            "diskette:20:Loading data from dump 'django-auth.json' (959 bytes)",
            "diskette:10:Installed 3 object(s) from 1 fixture(s)",
            "diskette:20:Loading data from dump 'django-site.json' (194 bytes)",
            "diskette:10:Installed 2 object(s) from 1 fixture(s)"
        ]
    ),
    (
        {
            "no_data": True,
            "no_storages": False,
        },
        [
            "diskette:20:=== Starting restoration ===",
            "diskette:10:diskette==0.0.0-test",
            "diskette:10:- Storages contents will be restored into: {tmp_path}",
            "diskette:10:Archive checksum: dummy-checksum",
            "diskette:10:Creating storage parent directory: {tmp_path}/storage_samples",
            (
                "diskette:20:Restoring storage directory (7.2 KB): storage_samples/"
                "storage-1"
            ),
            (
                "diskette:20:Restoring storage directory (9.6 KB): storage_samples/"
                "storage-2"
            ),
        ]
    ),
])
def test_load_options(caplog, settings, db, mocked_checksum, mocked_version,
                      tests_settings, tmp_path, options, expected):
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

    handler = LoadCommandHandler()
    handler.logger = LoggingOutput()

    stats = handler.load(
        archive_path,
        tmp_path,
        **options
    )

    assert archive_path.exists() is options.get("keep", False)

    # Query Site and User to check expected data from dumps
    if not options.get("no_data", False):
        user_app, user_model = settings.AUTH_USER_MODEL.split(".")
        User = apps.get_registered_model(user_app, user_model)
        assert User.objects.count() == 3
        assert Site.objects.count() == 2

    # Every storages should be present in destination and not empty
    if not options.get("no_storages", False):
        for source, stored in stats["storages"]:
            assert stored.exists() is True
            assert len(list(stored.iterdir())) > 0

    # Flatten logging messages
    logs = [
        name + ":" + str(lv) + ":" + msg
        for name, lv, msg in caplog.record_tuples
    ]

    assert logs == [
        # Add possible 'tmp_path' in case it is used
        item.format(tmp_path=tmp_path)
        for item in expected
    ]
