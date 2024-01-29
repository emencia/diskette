import os
import shutil
from io import StringIO
from pathlib import Path

from django.core import management
from django.apps import apps
from django.contrib.sites.models import Site


def test_load_cmd(caplog, db, settings, tests_settings, tmp_path):
    """
    Load command should respect arguments and restore contents from archive.
    """
    # Copy sample archive to temp dir
    archive_name = "basic_data_storages.tar.gz"
    archive_path = tmp_path / archive_name
    shutil.copy(
        tests_settings.fixtures_path / "archive_samples" / archive_name,
        archive_path
    )

    # Execute load command
    args = [
        "{}".format(archive_path),
        "--storages-basepath={}".format(tmp_path),
    ]
    out = StringIO()
    management.call_command("diskette_load", *args, stdout=out)
    # content = out.getvalue()
    out.close()

    # Ensure archive has been removed once done
    assert archive_path.exists() is False

    # Query Site and User to check expected data from dumps
    user_app, user_model = settings.AUTH_USER_MODEL.split(".")
    User = apps.get_registered_model(user_app, user_model)
    assert User.objects.count() == 1
    assert Site.objects.count() == 1

    # Collect deployed storages files as a list of relative paths
    storages_files = []
    for root, dirs, files in os.walk(tmp_path):
        storages_files.extend([
            str((Path(root) / item).relative_to(tmp_path))
            for item in files
        ])

    # Check collected paths match the expected storage files from archive
    assert sorted(storages_files) == [
        "storage_samples/storage-1/blue.png",
        "storage_samples/storage-1/plop/green.png",
        "storage_samples/storage-1/sample.txt",
        "storage_samples/storage-2/ping/grey.png",
        "storage_samples/storage-2/pong/sample.nope"
    ]
