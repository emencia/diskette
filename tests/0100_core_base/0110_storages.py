from pathlib import Path

import pytest

from diskette.core.storages import StorageManager
from diskette.exceptions import DumperError


def test_validate(tests_settings):
    """
    Storage path must be a Path object, exists and a directory else it should raise
    an error.
    """
    storage_samples = tests_settings.fixtures_path / "storage_samples"

    manager = StorageManager(storages=[
        storage_samples / "storage-1",
        storage_samples / "storage-2"
    ])
    manager.validate_storages()

    manager = StorageManager(storages=["nope"])
    with pytest.raises(DumperError) as excinfo:
        manager.validate_storages()

    assert str(excinfo.value) == "Storage path is not a 'pathlib.Path' object: nope"

    manager = StorageManager(storages=[storage_samples / "nope"])
    with pytest.raises(DumperError) as excinfo:
        manager.validate_storages()

    assert str(excinfo.value) == (
        "Storage path does not exist: {}/nope".format(
            storage_samples
        )
    )

    manager = StorageManager(storages=[storage_samples / "storage-1/sample.txt"])
    with pytest.raises(DumperError) as excinfo:
        manager.validate_storages()

    assert str(excinfo.value) == (
        "Storage path is not a directory: {}/storage-1/sample.txt".format(
            storage_samples
        )
    )


@pytest.mark.parametrize("excludes, expected", [
    (
        [],
        [
            "storage-1/blue.png",
            "storage-1/sample.txt",
            "storage-1/foo/foo_sample.txt",
            "storage-1/foo/grass.png",
            "storage-1/foo/bar/bar.nope",
            "storage-1/foo/bar/bar.txt",
            "storage-1/plop/green.png",
            "storage-2/pong/sample.nope",
            "storage-2/ping/grey.png"
        ],
    ),
    (
        ["*.nope"],
        [
            "storage-1/blue.png",
            "storage-1/sample.txt",
            "storage-1/foo/foo_sample.txt",
            "storage-1/foo/grass.png",
            "storage-1/foo/bar/bar.txt",
            "storage-1/plop/green.png",
            "storage-2/ping/grey.png"
        ],
    ),
    (
        ["foo/*.txt"],
        [
            "storage-1/blue.png",
            "storage-1/sample.txt",
            "storage-1/foo/grass.png",
            "storage-1/foo/bar/bar.nope",
            "storage-1/plop/green.png",
            "storage-2/pong/sample.nope",
            "storage-2/ping/grey.png"
        ],
    ),
    (
        ["foo/*"],
        [
            "storage-1/blue.png",
            "storage-1/sample.txt",
            "storage-1/plop/green.png",
            "storage-2/pong/sample.nope",
            "storage-2/ping/grey.png"
        ],
    ),
    (
        [
            "*.nope",
            "foo/*.txt",
            "*/green.png",
        ],
        [
            "storage-1/blue.png",
            "storage-1/sample.txt",
            "storage-1/foo/grass.png",
            "storage-2/ping/grey.png"
        ],
    ),
])
def test_iter_storages_files(settings, tests_settings, excludes, expected):
    """
    Files from storages should be listed depending possible exclude
    'Unix shell-style wildcards' filters.

    .. Note::

        Expected values are defined with a relative path which will be prefixed with
        'storage_samples' path during assertions.
    """
    storage_samples = tests_settings.fixtures_path / "storage_samples"
    relative_basepath = storage_samples.relative_to(Path.cwd())

    settings.DISKETTE_STORAGES = [
        storage_samples / "storage-1",
        storage_samples / "storage-2"
    ]

    manager = StorageManager(
        storages=[
            storage_samples / "storage-1",
            storage_samples / "storage-2"
        ],
        storages_excludes=excludes,
    )

    assert list(manager.iter_storages_files()) == [
        (storage_samples / path, relative_basepath / path)
        for path in expected
    ]
