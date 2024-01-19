from diskette.utils.filesystem import directory_size


def test_directory_size(tests_settings):
    """
    Function should recursively compute size of files and directories from path.
    """
    # Storages samples from tests
    storage_samples = tests_settings.fixtures_path / "storage_samples"
    storage_1 = storage_samples / "storage-1"
    storage_2 = storage_samples / "storage-2"

    assert directory_size(storage_1) == 17196
    assert directory_size(storage_2) == 9849
