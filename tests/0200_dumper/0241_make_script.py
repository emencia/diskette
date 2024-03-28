from pathlib import Path

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
def test_script(mocked_version, tmp_path, archive_initials):
    """
    No tarball should be created and command lines to dump datas should be print to
    standard output.
    """
    manager = Dumper(
        [
            ("Django auth", {"models": ["auth.Group", "auth.User"]}),
            ("Django site", {"models": ["sites"]}),
        ],
        storages=archive_initials["storages"]
    )
    manager.validate()
    lines = manager.make_script(Path("/home/foo")).split("\n")

    # Check expected archived files are all there with their expected size
    assert lines == [
        "# Django auth",
        "dumpdata auth.Group auth.User --output=/home/foo/django-auth.json",
        "# Django site",
        "dumpdata sites.Site --output=/home/foo/django-site.json"
    ]
