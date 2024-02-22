import shutil
from pathlib import Path

import pytest

from diskette.core.loader import Loader
from diskette.exceptions import DisketteError


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

    loader = Loader()
    try:
        extract_dir = loader.open(archive_path)

        assert sorted([str(v) for v in extract_dir.iterdir()]) == [
            "{}/data".format(extract_dir),
            "{}/manifest.json".format(extract_dir),
            "{}/storage_samples".format(extract_dir),
        ]
    finally:
        if extract_dir.exists():
            shutil.rmtree(extract_dir)


def test_manifest_invalid_path(tmp_path):
    """
    'get_manifest' method should raise an error when manifest path does not exist.
    """
    loader = Loader()

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

    loader = Loader()

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

    loader = Loader()

    with pytest.raises(DisketteError) as excinfo:
        loader.get_manifest(tmp_path)

    assert str(excinfo.value) == (
        "Dump archive is invalid, manifest does not include 'datas' field."
    )

    archive_path = tmp_path / "manifest.json"
    archive_path.write_text("{\"datas\": true}")

    loader = Loader()

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

    loader = Loader()
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
