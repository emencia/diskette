import json
import logging
import shutil
from pathlib import Path

import pytest
from freezegun import freeze_time

from diskette.core.loader import DumpLoader
from diskette.exceptions import DisketteError
from diskette.utils.loggers import LoggingOutput


@freeze_time("2012-10-15 10:00:00")
def test_open(caplog, manifest_version, tmp_path, tests_settings):
    """
    Archive should be correctly extracted into temp diskette directory.
    """
    archive_name = "basic_data_storages.tar.gz"
    archive_path = tmp_path / archive_name
    shutil.copy(
        tests_settings.fixtures_path / "archive_samples" / archive_name,
        archive_path
    )

    loader = DumpLoader()
    extracted = loader.open(archive_path)

    assert sorted([str(v) for v in extracted.iterdir()]) == [
        "{}/data".format(extracted),
        "{}/manifest.json".format(extracted),
        "{}/storage_samples".format(extracted),
    ]


def test_manifest_invalid_path(tmp_path):
    """
    'get_manifest' method should raise an error when manifest path does not exist.
    """
    loader = DumpLoader()

    with pytest.raises(DisketteError) as excinfo:
        loader.get_manifest(tmp_path / "nope")

    assert str(excinfo.value) == (
        "Dump archive is invalid, it does not include manifest file 'manifest.json'"
    )


def test_manifest_invalid_json(tmp_path):
    """
    'get_manifest' method should raise an error when manifest is not valid JSON.
    """
    archive_path = tmp_path / "manifest.json"
    archive_path.write_text("I'm not JSON")

    loader = DumpLoader()

    with pytest.raises(DisketteError) as excinfo:
        loader.get_manifest(tmp_path)

    assert str(excinfo.value) == (
        "Dump archive is invalid, included manifest file has invalid JSON "
        "syntax: Expecting value: line 1 column 1 (char 0)"
    )


def test_manifest_invalid_structure(tmp_path):
    """
    'get_manifest' method should raise an error when manifest don't have the expected
    manifest structure and content.
    """
    archive_path = tmp_path / "manifest.json"
    archive_path.write_text("{\"foo\": true}")

    loader = DumpLoader()

    with pytest.raises(DisketteError) as excinfo:
        loader.get_manifest(tmp_path)

    assert str(excinfo.value) == (
        "Dump archive is invalid, manifest does not include 'datas' field."
    )

    archive_path = tmp_path / "manifest.json"
    archive_path.write_text("{\"datas\": true}")

    loader = DumpLoader()

    with pytest.raises(DisketteError) as excinfo:
        loader.get_manifest(tmp_path)

    assert str(excinfo.value) == (
        "Dump archive is invalid, manifest does not include 'storages' field."
    )


def test_manifest(caplog, tmp_path, tests_settings):
    """
    Correct manifest should be returned.
    """
    manifest_path = tmp_path / "manifest.json"
    shutil.copy(
        tests_settings.fixtures_path / "manifest_samples" / "basic.json",
        manifest_path
    )

    loader = DumpLoader()
    manifest = loader.get_manifest(tmp_path)

    assert manifest == {
        "version": "0.0.0-test",
        "creation": "2012-10-15T10:00:00",
        "datas": [
            Path("data/djangocontribsites.json"),
            Path("data/djangocontribauth.json")
        ],
        "storages": [
            Path("storages/storage-1"),
            Path("storages/storage-2")
        ]
    }


@freeze_time("2012-10-15 10:00:00")
def test_deploy_storages(caplog, tmp_path, tests_settings):
    """
    Storages should be correctly deployed as expected into destination.
    """
    caplog.set_level(logging.DEBUG)

    # Storages samples from tests
    storage_samples = tests_settings.fixtures_path / "storage_samples"
    # Create dummy source tree
    sources = tmp_path / "sources"
    # Simulate an extracted archive with storages copied from tests samples
    archive = tmp_path / "archive"
    # Where the storages will be restored from archive
    destination = tmp_path / "destination"
    # Add an existing directory
    (destination / "storages/storage-1/foo").mkdir(parents=True)
    # Shared basic manifest
    manifest = {
        "version": "0.0.0-test",
        "creation": "2012-10-15T10:00:00",
        "datas": [],
        "storages": [
            Path("storages/storage-1"),
            Path("storages/storage-2")
        ]
    }

    # Copy storages samples in archive (loader moves the archive content so we can not
    # directly use the "storage_samples" content
    shutil.copytree(storage_samples, archive / "storages")

    # Deploy
    loader = DumpLoader(logger=LoggingOutput())
    extracted = loader.deploy_storages(
        archive,
        manifest,
        destination
    )

    assert caplog.record_tuples == [
        (
            "diskette", logging.DEBUG, (
                "Removing previous storage version directory: "
                "{}/storages/storage-1".format(destination)
            )
        ),
        ("diskette", logging.INFO, (
            "Restoring storage directory (16.8 KB): storages/storage-1"
        )),
        ("diskette", logging.INFO, (
            "Restoring storage directory (9.6 KB): storages/storage-2"
        )),
    ]

    # Every storages should be present in destination and not empty
    for item in manifest["storages"]:
        storage_path = destination / item
        assert storage_path.exists() is True
        assert len(list(storage_path.iterdir())) > 0


@pytest.mark.skip("When test_deploy_METHODS have been done")
@freeze_time("2012-10-15 10:00:00")
def test_deploy(caplog, tmp_path, tests_settings):
    """
    TODO: Archive data and storages dumps should be correctly deployed as expected.
    """
    caplog.set_level(logging.DEBUG)

    archive_name = "basic_data_storages.tar.gz"
    archive_path = tmp_path / archive_name
    shutil.copy(
        tests_settings.fixtures_path / "archive_samples" / archive_name,
        archive_path
    )

    loader = DumpLoader(logger=LoggingOutput())
    extracted = loader.deploy(archive_path, tmp_path)

    print("tmp_path.iterdir:", list(tmp_path.iterdir()))

    assert 1 == 42
