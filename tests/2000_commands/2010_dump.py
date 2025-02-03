import tarfile
from io import StringIO

import pytest

from django.core import management
from django.core.management.base import CommandError

from diskette.factories import DumpFileFactory
from diskette.models import DumpFile
from diskette.choices import STATUS_PROCESSED


def test_dump_cmd(caplog, db, tests_settings, tmp_path):
    """
    Dump command should respect arguments and build a proper dump archive.
    """
    appconf = tests_settings.fixtures_path / "basic_apps.json"
    storage_1 = tests_settings.fixtures_path / "storage_samples" / "storage-1"
    archive_path = tmp_path / "foo_data_storages.tar.gz"

    with StringIO() as out:
        args = [
            "--destination={}".format(tmp_path),
            "--appconf={}".format(appconf),
            "--storage={}".format(storage_1),
            "--filename=foo{features}.tar.gz",
            "--storages-exclude=*.nope",
        ]

        management.call_command("diskette_dump", *args, stdout=out)

    assert archive_path.exists() is True

    # Read archive members to get archived files
    with tarfile.open(archive_path, "r:gz") as archive:
        archived = [
            tarinfo.name
            for tarinfo in archive.getmembers()
            if tarinfo.isfile()
        ]

    # Check expected archived files are all there
    assert archived == [
        "data/djangocontribauth.json",
        "data/djangocontribsites.json",
        "tests/data_fixtures/storage_samples/storage-1/blue.png",
        "tests/data_fixtures/storage_samples/storage-1/sample.txt",
        "tests/data_fixtures/storage_samples/storage-1/foo/foo_sample.txt",
        "tests/data_fixtures/storage_samples/storage-1/foo/grass.png",
        "tests/data_fixtures/storage_samples/storage-1/foo/bar/bar.txt",
        "tests/data_fixtures/storage_samples/storage-1/plop/green.png",
        "manifest.json"
    ]


def test_dump_cmd_no_archive(caplog, db, tests_settings, tmp_path):
    """
    With 'no archive' mode the command should output command line to perform dump
    manually instead of automatically creating it.
    """
    appconf = tests_settings.fixtures_path / "basic_apps.json"
    storage_1 = tests_settings.fixtures_path / "storage_samples" / "storage-1"
    archive_path = tmp_path / "foo_data_storages.tar.gz"

    with StringIO() as out:
        args = [
            "--destination=/home/foo",
            "--appconf={}".format(appconf),
            "--storage={}".format(storage_1),
            "--filename=foo{features}.tar.gz",
            "--storages-exclude=*.nope",
            "--no-archive",
            "-v 0"
        ]

        management.call_command("diskette_dump", *args, stdout=out)
        content = out.getvalue()

    assert archive_path.exists() is False

    assert content.split("\n") == [
        "# django.contrib.sites",
        (
            "dumpdata sites.Site --natural-foreign --output=/home/foo/"
            "djangocontribsites.json"
        ),
        "# django.contrib.auth",
        (
            "dumpdata auth.Group auth.User --natural-foreign --output=/home/foo/"
            "djangocontribauth.json"
        ),
        ""
    ]


def test_dump_cmd_check(caplog, db, tests_settings, tmp_path):
    """
    Check mode should output debug informations without creating archive file.
    """
    appconf = tests_settings.fixtures_path / "basic_apps.json"
    storage_1 = tests_settings.fixtures_path / "storage_samples" / "storage-1"
    archive_path = tmp_path / "foo_data_storages.tar.gz"

    with StringIO() as out:
        args = [
            "--destination={}".format(tmp_path),
            "--appconf={}".format(appconf),
            "--storage={}".format(storage_1),
            "--filename=foo{features}.tar.gz",
            "--storages-exclude=*.nope",
            "--check",
        ]

        management.call_command("diskette_dump", *args, stdout=out)
        content = out.getvalue()

    assert archive_path.exists() is False

    assert content.split("\n") == [
        "=== Starting to check ===",
        "Dumping data for application 'django.contrib.sites'",
        "Dumping data for application 'django.contrib.auth'",
        "- Scanning storages to archive",
        "- 6 file(s) would be collected for a total of 4.8 KB",
        "Dump archive would be created at: {}".format(archive_path),
        ""
    ]


def test_dump_cmd_incompatible_save(db, settings):
    """
    Save mode is incompatible with check, no archive and disabled admin.
    """
    with StringIO() as out:
        args = [
            "--check",
            "--save",
        ]

        with pytest.raises(CommandError) as excinfo:
            management.call_command("diskette_dump", *args, stdout=out)

        assert str(excinfo.value) == (
            "The option '--save' is incompatible with options '--check', "
            "'--no-archive' and disabled admin from setting 'DISKETTE_ADMIN_ENABLED'."
        )

    with StringIO() as out:
        args = [
            "--no-archive",
            "--save",
        ]

        with pytest.raises(CommandError) as excinfo:
            management.call_command("diskette_dump", *args, stdout=out)

        assert str(excinfo.value) == (
            "The option '--save' is incompatible with options '--check', "
            "'--no-archive' and disabled admin from setting 'DISKETTE_ADMIN_ENABLED'."
        )

    settings.DISKETTE_ADMIN_ENABLED = False
    with StringIO() as out:
        args = [
            "--save",
        ]

        with pytest.raises(CommandError) as excinfo:
            management.call_command("diskette_dump", *args, stdout=out)

        assert str(excinfo.value) == (
            "The option '--save' is incompatible with options '--check', "
            "'--no-archive' and disabled admin from setting 'DISKETTE_ADMIN_ENABLED'."
        )


def test_dump_cmd_save(caplog, db, tests_settings, tmp_path):
    """
    Save option should trigger creation of a DumpFile object related to created
    archive and should run automatic depreciation routine and depreciated object purge.
    """
    appconf = tests_settings.fixtures_path / "basic_apps.json"
    archive_path = tmp_path / "foo_data.tar.gz"

    # Create some dump objects before running command
    DumpFileFactory(deprecated=True, path="foo")
    DumpFileFactory(deprecated=False, path="bar", with_storage=False)

    with StringIO() as out:
        args = [
            "--destination={}".format(tmp_path),
            "--appconf={}".format(appconf),
            "--no-storages",
            "--filename=foo{features}.tar.gz",
            "--save"
        ]

        management.call_command("diskette_dump", *args, stdout=out)

    # Archive file has been created
    assert archive_path.exists() is True
    # Depreciation and purge routines have been runned
    assert DumpFile.objects.filter(deprecated=False).count() == 1
    assert DumpFile.objects.filter(path__startswith="removed:/").count() == 2

    # Check create dump object is correct
    latest = DumpFile.objects.latest("processed")
    msg = "Dump archive was created at: {}".format(archive_path)
    assert msg in latest.logs
    assert latest.with_data is True
    assert latest.with_storage is False
    assert latest.status == STATUS_PROCESSED
    assert latest.path == str(archive_path.name)
    assert latest.size > 0
