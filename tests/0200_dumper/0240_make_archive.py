import tarfile

import pytest
from freezegun import freeze_time

from diskette.core.dumper import Dumper
from diskette.factories import UserFactory


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
def test_archive_data(manifest_version, tmp_path, archive_initials):
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
    assert archived == [
        ("data/django-auth.json", 328),
        ("data/django-site.json", 94),
        ("manifest.json", 139),
    ]

    assert archive_path.name == "foo_data.tar.gz"


@freeze_time("2012-10-15 10:00:00")
def test_archive_storages(manifest_version, tmp_path, archive_initials):
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
    assert archived == [
        ("tests/data_fixtures/storage_samples/storage-1/blue.png", 1543),
        ("tests/data_fixtures/storage_samples/storage-1/sample.txt", 11),
        ("tests/data_fixtures/storage_samples/storage-1/foo/foo_sample.txt", 3),
        ("tests/data_fixtures/storage_samples/storage-1/foo/grass.png", 1659),
        ("tests/data_fixtures/storage_samples/storage-1/foo/bar/bar.nope", 8),
        ("tests/data_fixtures/storage_samples/storage-1/foo/bar/bar.txt", 3),
        ("tests/data_fixtures/storage_samples/storage-1/plop/green.png", 1681),
        ("tests/data_fixtures/storage_samples/storage-2/pong/sample.nope", 11),
        ("tests/data_fixtures/storage_samples/storage-2/ping/grey.png", 1646),
        ("manifest.json", 187),
    ]

    assert archive_path.name == "foo_storages.tar.gz"


@freeze_time("2012-10-15 10:00:00")
def test_archive_all(manifest_version, tmp_path, archive_initials):
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
    assert archived == [
        ("data/django-auth.json", 328),
        ("data/django-site.json", 94),
        ("tests/data_fixtures/storage_samples/storage-1/blue.png", 1543),
        ("tests/data_fixtures/storage_samples/storage-1/sample.txt", 11),
        ("tests/data_fixtures/storage_samples/storage-1/foo/foo_sample.txt", 3),
        ("tests/data_fixtures/storage_samples/storage-1/foo/grass.png", 1659),
        ("tests/data_fixtures/storage_samples/storage-1/foo/bar/bar.nope", 8),
        ("tests/data_fixtures/storage_samples/storage-1/foo/bar/bar.txt", 3),
        ("tests/data_fixtures/storage_samples/storage-1/plop/green.png", 1681),
        ("tests/data_fixtures/storage_samples/storage-2/pong/sample.nope", 11),
        ("tests/data_fixtures/storage_samples/storage-2/ping/grey.png", 1646),
        ("manifest.json", 233),
    ]

    assert archive_path.name == "foo_data_storages.tar.gz"


@freeze_time("2012-10-15 10:00:00")
def test_archive_excludes(manifest_version, tmp_path, archive_initials):
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
    assert archived == [
        ("data/django-auth.json", 328),
        ("data/django-site.json", 94),
        ("tests/data_fixtures/storage_samples/storage-1/blue.png", 1543),
        ("tests/data_fixtures/storage_samples/storage-1/sample.txt", 11),
        ("tests/data_fixtures/storage_samples/storage-1/foo/grass.png", 1659),
        ("tests/data_fixtures/storage_samples/storage-2/ping/grey.png", 1646),
        ("manifest.json", 233),
    ]
