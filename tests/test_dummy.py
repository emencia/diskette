import json
import tarfile
import logging

import pytest
from freezegun import freeze_time

from diskette.utils.factories import UserFactory
from diskette.utils.loggers import LoggingOutput
from diskette.core.handlers import DumpCommandHandler


@pytest.mark.skip("Only to be used during test development")
@freeze_time("2012-10-15 10:00:00")
def test_create_fixture_basic_tarball(caplog, tests_settings, db, tmp_path):
    """
    A temporary script to create the 'basic_data_storages.tar.gz' fixture tarball.
    """
    caplog.set_level(logging.DEBUG)

    storage_samples = tests_settings.fixtures_path / "storage_samples"

    # Create users
    picsou = UserFactory(first_name="Picsou", last_name="Balthazar", username="picsou")
    picsou.password = "dummy"
    picsou.save()

    commander = DumpCommandHandler()
    commander.logger = LoggingOutput()

    tarball = commander.dump(
        tmp_path,
        application_configurations=[
            ("Django auth", {"models": ["auth.group", "auth.user"]}),
            ("Django site", {"models": ["sites"]}),
        ],
        storages=[
            storage_samples / "storage-1",
            storage_samples / "storage-2"
        ],
        storages_basepath=tests_settings.fixtures_path,
        storages_excludes=["foo/*"],
        tarball_filename="basic{features}.tar.gz",
    )

    # Read tarball members to get archived files
    with tarfile.open(tarball, "r:gz") as archive:
        archived = [
            (tarinfo.name, tarinfo.size)
            for tarinfo in archive.getmembers()
            if tarinfo.isfile()
        ]

    print()
    print(json.dumps(archived, indent=4))
    print()

    assert 1 == 42
