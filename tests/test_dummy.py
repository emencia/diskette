"""
.. Warning::
    These are development scripts to create archive fixtures. They are in tests as a
    convenience to easily use factories.

    They must only be enabled when needed to rebuild archive fixtures because we aim to
    have stable data fixtures, but some code change may need to rebuild them
    occasionally.

    Once runned, they should fail only on the ``assert 1 == 42``, you should copy
    the created archive path to move it at your current directory, then copy it data
    dump files to ``data_fixtures/data_samples/`` and then copy the archives to
    ``data_fixtures/archive_samples/``. Finally uncomment the ``pytest.skip`` lines,
    run again the full test suites and when it is ok comment again the ``pytest.skip``
    lines.
"""

import json
import tarfile
import logging

import pytest
from freezegun import freeze_time

from django.contrib.sites.models import Site

from diskette.factories import UserFactory
from diskette.utils.loggers import LoggingOutput
from diskette.core.handlers import DumpCommandHandler

from sandbox.djangoapp_sample.factories import (
    ArticleFactory, BlogFactory, CategoryFactory
)


# Comment this to enable rebuilding archives, but beware to uncomment before any commit
pytest.skip(
    "Only to be used during test development",
    allow_module_level=True
)


@freeze_time("2012-10-15 10:00:00")
def test_create_fixture_basic_tarball(caplog, db, mocked_version, tests_settings,
                                      tmp_path):
    """
    Development script to create the 'basic_data_storages.tar.gz' archive fixture.
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
            ("Django auth", {
                "models": ["auth.group", "auth.user"],
                "natural_foreign": True,
            }),
            ("Django site", {
                "models": ["sites"],
                "natural_foreign": True,
            }),
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

    # The test must fail to see logs and created archive file path
    assert 1 == 42


@freeze_time("2012-10-15 10:00:00")
def test_create_fixture_advanced_tarball(caplog, db, mocked_version, tests_settings,
                                         tmp_path):
    """
    Development script to create the 'advanced_data_storages.tar.gz' archive fixture.
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

    # Create blog stuff
    blog_1 = BlogFactory()
    blog_2 = BlogFactory()
    cat_1 = CategoryFactory()
    cat_2 = CategoryFactory()
    ArticleFactory(blog=blog_1, author=picsou, fill_categories=[cat_1, cat_2])
    ArticleFactory(blog=blog_1, author=picsou)
    ArticleFactory(blog=blog_2, author=None, fill_categories=[cat_1])

    # Add a Site object in addition of the default one from Site migration
    new_site = Site(name="The batcave", domain="batcave.localhost")
    new_site.save()

    commander = DumpCommandHandler()
    commander.logger = LoggingOutput()

    tarball = commander.dump(
        tmp_path,
        application_configurations=[
            ("Django auth", {
                "models": ["auth.group", "auth.user"],
                "natural_foreign": True,
            }),
            ("Django site", {
                "models": ["sites"],
                "natural_foreign": True,
            }),
            ("Blog sample", {
                "models": ["djangoapp_sample"],
                "natural_foreign": True,
            }),
        ],
        storages=[
            storage_samples / "storage-1",
            storage_samples / "storage-2"
        ],
        storages_basepath=tests_settings.fixtures_path,
        storages_excludes=["foo/*"],
        archive_filename="advanced{features}.tar.gz",
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

    # The test must fail to see logs and created archive file path
    assert 1 == 42
