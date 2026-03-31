import tarfile

import pytest
from freezegun import freeze_time

from django import VERSION as django_version

from diskette.core.dumper import Dumper
from diskette.factories import UserFactory


# Dump file sizes before Django 6
DJANGO_PRE_6_DUMPFILES = [
    ("data/django-auth.json", 328),
    ("data/django-site.json", 94),
]


# Dump file sizes before Django 6
DJANGO_6_DUMPFILES = [
    ("data/django-auth.json", 329),
    ("data/django-site.json", 95),
]


@pytest.fixture(scope="function")
def archive_initials(tests_settings, db):
    """
    Fixture to create common initial datas and settings for archive testing
    """
    storage_samples = tests_settings.fixtures_path / "storage_samples"

    # Force values to ensure object size is always the same in dump
    picsou = UserFactory(first_name="Picsou", last_name="Balthazar", username="picsou")
    picsou.password = "dummy"
    picsou.save()

    return {
        "storage_samples_path": storage_samples,
        "storages": [
            storage_samples / "storage-1",
            storage_samples / "storage-2"
        ],
        "user": picsou,
    }


@freeze_time("2012-10-15 10:00:00")
def test_archive_data(mocked_version, tmp_path, archive_initials):
    """
    Tarball should be created with data dumps only.
    """
    manager = Dumper(
        [
            ("Django site", {"models": ["sites"]}),
            ("Django auth", {"models": ["auth.Group", "auth.User"]}),
        ],
        storages=archive_initials["storages"],
    )
    manager.validate()
    archive_path = manager.make_archive(
        tmp_path,
        "foo{features}.tar.gz",
        with_storages=False
    )

    # Read archive members to get archived files
    with tarfile.open(archive_path, "r:gz") as archive:
        archived = [
            (tarinfo.name, tarinfo.size)
            for tarinfo in archive.getmembers()
            if tarinfo.isfile()
        ]

    # Check expected archived files are all there with their expected size
    expected_dumps = (
        DJANGO_PRE_6_DUMPFILES if django_version[0] < 6 else DJANGO_6_DUMPFILES
    )
    assert sorted(archived) == expected_dumps + [
        ("manifest.json", 139),
    ]

    assert archive_path.name == "foo_data.tar.gz"


@freeze_time("2012-10-15 10:00:00")
def test_archive_storages(mocked_version, tmp_path, archive_initials):
    """
    Tarball should be created with storages dumps only.
    """
    manager = Dumper([], storages=archive_initials["storages"])
    manager.validate()
    archive_path = manager.make_archive(
        tmp_path,
        "foo{features}.tar.gz",
        with_data=False
    )

    # Read archive members to get archived files
    with tarfile.open(archive_path, "r:gz") as archive:
        archived = [
            (tarinfo.name, tarinfo.size)
            for tarinfo in archive.getmembers()
            if tarinfo.isfile()
        ]

    # Check expected archived files are all there with their expected size
    assert sorted(archived) == [
        ("manifest.json", 187),
        ("tests/data_fixtures/storage_samples/storage-1/blue.png", 1543),
        ("tests/data_fixtures/storage_samples/storage-1/foo/bar/bar.nope", 8),
        ("tests/data_fixtures/storage_samples/storage-1/foo/bar/bar.txt", 3),
        ("tests/data_fixtures/storage_samples/storage-1/foo/foo_sample.txt", 3),
        ("tests/data_fixtures/storage_samples/storage-1/foo/grass.png", 1659),
        ("tests/data_fixtures/storage_samples/storage-1/plop/green.png", 1681),
        ("tests/data_fixtures/storage_samples/storage-1/sample.txt", 11),
        ("tests/data_fixtures/storage_samples/storage-2/ping/grey.png", 1646),
        ("tests/data_fixtures/storage_samples/storage-2/pong/sample.nope", 11),
    ]

    assert archive_path.name == "foo_storages.tar.gz"


@freeze_time("2012-10-15 10:00:00")
def test_archive_all(mocked_version, tmp_path, archive_initials):
    """
    Tarball should be created with every dumps.
    """
    manager = Dumper(
        [
            ("Django auth", {"models": ["auth.Group", "auth.User"]}),
            ("Django site", {"models": ["sites"]}),
        ],
        storages=archive_initials["storages"]
    )
    manager.validate()
    archive_path = manager.make_archive(
        tmp_path,
        "foo{features}.tar.gz",
    )

    # Read archive members to get archived files
    with tarfile.open(archive_path, "r:gz") as archive:
        archived = [
            (tarinfo.name, tarinfo.size)
            for tarinfo in archive.getmembers()
            if tarinfo.isfile()
        ]

    # print()
    # print(json.dumps(archived, indent=4))
    # print()

    # Check expected archived files are all there with their expected size
    expected_dumps = (
        DJANGO_PRE_6_DUMPFILES if django_version[0] < 6 else DJANGO_6_DUMPFILES
    )
    assert sorted(archived) == expected_dumps + [
        ("manifest.json", 233),
        ("tests/data_fixtures/storage_samples/storage-1/blue.png", 1543),
        ("tests/data_fixtures/storage_samples/storage-1/foo/bar/bar.nope", 8),
        ("tests/data_fixtures/storage_samples/storage-1/foo/bar/bar.txt", 3),
        ("tests/data_fixtures/storage_samples/storage-1/foo/foo_sample.txt", 3),
        ("tests/data_fixtures/storage_samples/storage-1/foo/grass.png", 1659),
        ("tests/data_fixtures/storage_samples/storage-1/plop/green.png", 1681),
        ("tests/data_fixtures/storage_samples/storage-1/sample.txt", 11),
        ("tests/data_fixtures/storage_samples/storage-2/ping/grey.png", 1646),
        ("tests/data_fixtures/storage_samples/storage-2/pong/sample.nope", 11),
    ]

    assert archive_path.name == "foo_data_storages.tar.gz"


@freeze_time("2012-10-15 10:00:00")
def test_archive_excludes(mocked_version, tmp_path, archive_initials):
    """
    Tarball should be created with every dumps and properly follow excluding filters
    when collecting storage files.
    """
    manager = Dumper(
        [
            ("Django site", {"models": ["sites"]}),
            ("Django auth", {"models": ["auth.Group", "auth.User"]}),
        ],
        storages=archive_initials["storages"],
        storages_excludes=[
            "*.nope",
            "foo/*.txt",
            "*/green.png",
        ],
    )
    manager.validate()
    archive_path = manager.make_archive(
        tmp_path,
        "foo{features}.tar.gz",
    )

    # Read archive members to get archived files
    with tarfile.open(archive_path, "r:gz") as archive:
        archived = [
            (tarinfo.name, tarinfo.size)
            for tarinfo in archive.getmembers()
            if tarinfo.isfile()
        ]

    # Check expected archived files are all there with their expected size
    expected_dumps = (
        DJANGO_PRE_6_DUMPFILES if django_version[0] < 6 else DJANGO_6_DUMPFILES
    )
    assert sorted(archived) == expected_dumps + [
        ("manifest.json", 233),
        ("tests/data_fixtures/storage_samples/storage-1/blue.png", 1543),
        ("tests/data_fixtures/storage_samples/storage-1/foo/grass.png", 1659),
        ("tests/data_fixtures/storage_samples/storage-1/sample.txt", 11),
        ("tests/data_fixtures/storage_samples/storage-2/ping/grey.png", 1646),
    ]
