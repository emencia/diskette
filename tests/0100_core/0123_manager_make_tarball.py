import tarfile

import pytest
from freezegun import freeze_time

from diskette.core.manager import DumpManager
from diskette.utils.factories import UserFactory


@pytest.fixture(scope="function")
def tarball_initials(tests_settings, db):
    """
    Fixture to create common initial datas and settings for tarball testing
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
def test_tarball_data(tmp_path, tarball_initials):
    """
    Tarball should be created with data dumps only.
    """
    manager = DumpManager(
        [
            ("Django site", {"models": ["sites"]}),
            ("Django auth", {"models": ["auth.group", "auth.user"]}),
        ],
        storages=tarball_initials["storages"],
    )
    manager.validate()
    tarball_path = manager.make_tarball(
        tmp_path,
        "foo{features}.tar.gz",
        with_storages=False
    )

    # Read tarball members to get archived files
    with tarfile.open(tarball_path, "r:gz") as archive:
        archived = [
            (tarinfo.name, tarinfo.size)
            for tarinfo in archive.getmembers()
            if tarinfo.isfile()
        ]

    # Check expected archived files are all there with their expected size
    assert archived == [
        ("data/django-auth.json", 328),
        ("data/django-site.json", 94),
        ("manifest.json", 134),
    ]

    assert tarball_path.name == "foo_data.tar.gz"


@freeze_time("2012-10-15 10:00:00")
def test_tarball_storages(tmp_path, tarball_initials):
    """
    Tarball should be created with storages dumps only.
    """
    manager = DumpManager([], storages=tarball_initials["storages"])
    manager.validate()
    tarball_path = manager.make_tarball(
        tmp_path,
        "foo{features}.tar.gz",
        with_data=False
    )

    # Read tarball members to get archived files
    with tarfile.open(tarball_path, "r:gz") as archive:
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
        ("manifest.json", 182),
    ]

    assert tarball_path.name == "foo_storages.tar.gz"


@freeze_time("2012-10-15 10:00:00")
def test_tarball_all(tmp_path, tarball_initials):
    """
    Tarball should be created with every dumps.
    """
    manager = DumpManager(
        [
            ("Django auth", {"models": ["auth.group", "auth.user"]}),
            ("Django site", {"models": ["sites"]}),
        ],
        storages=tarball_initials["storages"]
    )
    manager.validate()
    tarball_path = manager.make_tarball(
        tmp_path,
        "foo{features}.tar.gz",
    )

    # Read tarball members to get archived files
    with tarfile.open(tarball_path, "r:gz") as archive:
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
        ("manifest.json", 228),
    ]

    assert tarball_path.name == "foo_data_storages.tar.gz"


@freeze_time("2012-10-15 10:00:00")
def test_tarball_excludes(tmp_path, tarball_initials):
    """
    Tarball should be created with every dumps and properly follow excluding filters
    when collecting storage files.
    """
    manager = DumpManager(
        [
            ("Django site", {"models": ["sites"]}),
            ("Django auth", {"models": ["auth.group", "auth.user"]}),
        ],
        storages=tarball_initials["storages"],
        storages_excludes=[
            "*.nope",
            "foo/*.txt",
            "*/green.png",
        ],
    )
    manager.validate()
    tarball_path = manager.make_tarball(
        tmp_path,
        "foo{features}.tar.gz",
    )

    # Read tarball members to get archived files
    with tarfile.open(tarball_path, "r:gz") as archive:
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
        ("tests/data_fixtures/storage_samples/storage-1/foo/grass.png", 1659),
        ("tests/data_fixtures/storage_samples/storage-2/ping/grey.png", 1646),
        ("manifest.json", 228),
    ]
