import shutil

import pytest
import requests

from diskette.exceptions import DisketteError
from diskette.core.loader import Loader


def test_open_download_success(caplog, requests_mock, tmp_path, tests_settings):
    """
    Method should correctly download archive file.
    """
    destination = tmp_path / "downloaded.tar.gz"

    url = "http://foo/basic_data_storages.tar.gz"
    requests_mock.get(url, text="faked file")

    loader = Loader()
    loader.download_archive(url, destination=destination)
    assert destination.read_text() == "faked file"


def test_open_download_error(caplog, requests_mock, tmp_path, tests_settings):
    """
    Encountered HTTP errors should be raised during operation.
    """
    destination = tmp_path / "downloaded.tar.gz"

    url = "http://foo/basic_data_storages.tar.gz"
    # requests_mock.get(url, exc=requests.exceptions.ConnectTimeout)
    requests_mock.get(url, status_code=500, text="some error")

    loader = Loader()
    with pytest.raises(requests.exceptions.HTTPError):
        loader.download_archive(url, destination=destination)


def test_open_file(caplog, mocked_version, tmp_path, tests_settings):
    """
    Local archive file should be correctly extracted into temp diskette directory.
    """
    archive_name = "basic_data_storages.tar.gz"
    archive_path = tmp_path / archive_name
    shutil.copy(
        tests_settings.fixtures_path / "archive_samples" / archive_name,
        archive_path
    )

    loader = Loader()
    extract_archive = None
    try:
        extract_archive = loader.open(archive_path)

        assert sorted([str(v) for v in extract_archive.iterdir()]) == [
            "{}/data".format(extract_archive),
            "{}/manifest.json".format(extract_archive),
            "{}/storage_samples".format(extract_archive),
        ]
    finally:
        if extract_archive and extract_archive.exists():
            shutil.rmtree(extract_archive)


def test_open_url(caplog, mocked_version, requests_mock, tmp_path, tests_settings):
    """
    Archive from an URL should be correctly downloaded then extracted into temp
    diskette directory.
    """
    archive_name = "basic_data_storages.tar.gz"
    archive_path = tmp_path / archive_name
    shutil.copy(
        tests_settings.fixtures_path / "archive_samples" / archive_name,
        archive_path
    )

    url = "http://foo/basic_data_storages.tar.gz"
    requests_mock.get(url, body=archive_path.open("rb"))

    loader = Loader()
    extract_archive = None
    try:
        extract_archive = loader.open(
            url,
            download_destination=tmp_path / "downloaded.tar.gz"
        )

        assert sorted([str(v) for v in extract_archive.iterdir()]) == [
            "{}/data".format(extract_archive),
            "{}/manifest.json".format(extract_archive),
            "{}/storage_samples".format(extract_archive),
        ]
    finally:
        if extract_archive and extract_archive.exists():
            shutil.rmtree(extract_archive)


def test_open_checksum(caplog, requests_mock, tmp_path, tests_settings):
    """
    When source checksum is given, operation should fail with an error if checksum
    comparison fails.
    """
    url = "http://foo/basic_data_storages.tar.gz"
    requests_mock.get(url, text="faked file")

    loader = Loader()
    extract_archive = None
    try:
        with pytest.raises(DisketteError) as excinfo:
            extract_archive = loader.open(
                url,
                download_destination=tmp_path / "downloaded.tar.gz",
                checksum="Nope",
            )

        assert str(excinfo.value) == (
            "Checksums do not match. Your archive file is probably corrupted."
        )
    finally:
        if extract_archive and extract_archive.exists():
            shutil.rmtree(extract_archive)
