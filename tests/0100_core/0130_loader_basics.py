import json
import shutil

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

    assert [str(v) for v in extracted.iterdir()] == [
        "{}/data".format(extracted),
        "{}/var".format(extracted),
        "{}/manifest.json".format(extracted),
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
    TODO: Correct manifest should be returned
    """
    manifest_path = tmp_path / "manifest.json"
    shutil.copy(
        tests_settings.fixtures_path / "manifest_samples" / "basic.json",
        manifest_path
    )

    print()
    print(list(tmp_path.iterdir()))
    print()

    loader = DumpLoader()
    manifest = loader.get_manifest(tmp_path)

    assert 1 == 42


@freeze_time("2012-10-15 10:00:00")
def test_deploy(caplog, tmp_path, tests_settings):
    """
    TODO: Archive contents should be correctly deployed as expected.
    """
    archive_name = "basic_data_storages.tar.gz"
    archive_path = tmp_path / archive_name
    shutil.copy(
        tests_settings.fixtures_path / "archive_samples" / archive_name,
        archive_path
    )

    loader = DumpLoader()
    extracted = loader.deploy(archive_path, tmp_path)

    assert 1 == 42
