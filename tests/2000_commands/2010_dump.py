import tarfile
from io import StringIO


from django.core import management


def test_dump_cmd(caplog, db, settings, tests_settings, tmp_path):
    """
    Dump command should respect arguments and build a proper dump archive.
    """
    appconf = tests_settings.fixtures_path / "basic_apps.json"
    storage_1 = tests_settings.fixtures_path / "storage_samples" / "storage-1"
    archive_path = tmp_path / "foo_data_storages.tar.gz"

    out = StringIO()

    args = [
        "--destination={}".format(tmp_path),
        "--appconf={}".format(appconf),
        "--storage={}".format(storage_1),
        "--filename=foo{features}.tar.gz",
        "--storages-exclude=*.nope",
    ]

    management.call_command("diskette_dump", *args, stdout=out)
    # content = out.getvalue()
    out.close()

    assert archive_path.exists() is True

    # Read archive members to get archived files
    with tarfile.open(archive_path, "r:gz") as archive:
        archived = [
            tarinfo.name
            for tarinfo in archive.getmembers()
            if tarinfo.isfile()
        ]

    # Check expected archived files are all there
    assert archived == [
        "data/djangocontribauth.json",
        "data/djangocontribsites.json",
        "tests/data_fixtures/storage_samples/storage-1/blue.png",
        "tests/data_fixtures/storage_samples/storage-1/sample.txt",
        "tests/data_fixtures/storage_samples/storage-1/foo/foo_sample.txt",
        "tests/data_fixtures/storage_samples/storage-1/foo/grass.png",
        "tests/data_fixtures/storage_samples/storage-1/foo/bar/bar.txt",
        "tests/data_fixtures/storage_samples/storage-1/plop/green.png",
        "manifest.json"
    ]
