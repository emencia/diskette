import shutil
from io import StringIO

from django.core import management
from django.apps import apps
from django.contrib.sites.models import Site

import pytest


@pytest.mark.skip("Unfinished yet, test load handler before")
def test_load_cmd(caplog, db, settings, tests_settings, tmp_path):
    """
    Load command should respect arguments and restore contents from archive.
    """
    archive_name = "basic_data_storages.tar.gz"
    archive_path = tmp_path / archive_name
    shutil.copy(
        tests_settings.fixtures_path / "archive_samples" / archive_name,
        archive_path
    )

    out = StringIO()

    args = [
        "{}".format(archive_path),
        "--storages-basepath={}".format(tmp_path),
    ]

    management.call_command("diskette_load", *args, stdout=out)
    content = out.getvalue()
    out.close()

    print(content)

    assert archive_path.exists() is False

    # Query Site and User to check expected data from dumps
    user_app, user_model = settings.AUTH_USER_MODEL.split(".")
    User = apps.get_registered_model(user_app, user_model)
    assert User.objects.count() == 1
    assert Site.objects.count() == 1

    # TODO: Check storages
    assert list(tmp_path.iterdir()) == []
