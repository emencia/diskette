import logging
import shutil
from pathlib import Path

from diskette.core.loader import Loader
from diskette.utils.loggers import LoggingOutput


def test_deploy_storages(caplog, tmp_path, tests_settings):
    """
    Storages should be correctly deployed as expected into destination.
    """
    caplog.set_level(logging.DEBUG)

    # Storages samples from tests
    storage_samples = tests_settings.fixtures_path / "storage_samples"
    # Simulate an extracted archive with storages copied from tests samples
    archive = tmp_path / "archive"
    # Where the storages will be restored from archive
    destination = tmp_path / "destination"
    # Add an existing directory to involve "existing directory" management
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

    # Copy storages samples in archive (to bypass loader which moves the archive
    # content that would destroy "storage_samples" content from test fixtures)
    shutil.copytree(storage_samples, archive / "storages")

    # Deploy storages
    loader = Loader(logger=LoggingOutput())
    loader.deploy_storages(
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
