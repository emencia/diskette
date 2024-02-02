import json
import tarfile
import logging

import pytest
from freezegun import freeze_time

from django.contrib.sites.models import Site

from diskette.factories import UserFactory
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
    sarah = UserFactory(
        first_name="Sarah", last_name="Connor", username="sarah",
        flag_is_superuser=True
    )
    sarah.password = "dummy"
    sarah.save()
    picsou = UserFactory(first_name="Picsou", last_name="Balthazar", username="picsou")
    picsou.password = "dummy"
    picsou.save()
    donald = UserFactory(first_name="Donald", last_name="Duck", username="donald")
    donald.password = "dummy"
    donald.save()

    # Add a Site object in addition of the default one from Site migration
    new_site = Site(name="The batcave", domain="batcave.localhost")
    new_site.save()

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
        archive_filename="basic{features}.tar.gz",
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
