import logging
import shutil

from freezegun import freeze_time

from django.apps import apps
from django.contrib.sites.models import Site

from diskette.core.loader import Loader
from diskette.utils.loggers import LoggingOutput


@freeze_time("2012-10-15 10:00:00")
def test_deploy(caplog, db, settings, tests_settings, tmp_path):
    """
    Archive data and storages dumps should be correctly deployed as expected.
    """
    caplog.set_level(logging.DEBUG)

    archive_name = "basic_data_storages.tar.gz"
    archive_path = tmp_path / archive_name
    shutil.copy(
        tests_settings.fixtures_path / "archive_samples" / archive_name,
        archive_path
    )

    loader = Loader(logger=LoggingOutput())
    deployed = loader.deploy(archive_path, tmp_path)

    # Every storages should be present in destination and not empty
    for source, stored in deployed["storages"]:
        assert stored.exists() is True
        assert len(list(stored.iterdir())) > 0

    # Query Site and User to check expected data from dumps
    user_app, user_model = settings.AUTH_USER_MODEL.split(".")
    User = apps.get_registered_model(user_app, user_model)
    assert User.objects.count() == 3
    assert Site.objects.count() == 2
