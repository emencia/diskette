import json
import logging
import shutil
from pathlib import Path

from freezegun import freeze_time

from django.apps import apps
from django.contrib.sites.models import Site

from diskette.core.loader import Loader
from diskette.utils.loggers import LoggingOutput


@freeze_time("2012-10-15 10:00:00")
def test_deploy_datas(caplog, db, tmp_path, settings, tests_settings):
    """
    Method should load data fixtures from extracted archive.
    """
    caplog.set_level(logging.DEBUG)

    # Data dump samples from tests
    data_samples = tests_settings.fixtures_path / "data_samples"
    # Simulate an extracted archive with storages copied from tests samples
    archive = tmp_path / "archive"
    # Create dummy source dir where to hold data dumps
    sources = archive / "sources"
    shutil.copytree(data_samples, sources)

    # Craft a basic manifest
    manifest = {
        "version": "0.0.0-test",
        "creation": "2012-10-15T10:00:00",
        "datas": [
            Path("sources/django-site.json"),
            Path("sources/django-auth.json"),
        ],
        "storages": []
    }

    # Deploy
    loader = Loader(logger=LoggingOutput())
    loader.deploy_datas(archive, manifest)

    # Flatten logging messages
    logs = [
        name + ":" + str(lv) + ":" + msg
        for name, lv, msg in caplog.record_tuples
    ]

    assert logs == [
        "diskette:20:Loading data from dump 'django-site.json' (194 bytes)",
        "diskette:10:Installed 2 object(s) from 1 fixture(s)",
        "diskette:20:Loading data from dump 'django-auth.json' (959 bytes)",
        "diskette:10:Installed 3 object(s) from 1 fixture(s)",
    ]

    # Query Site and User to check expected data from dumps
    user_app, user_model = settings.AUTH_USER_MODEL.split(".")
    User = apps.get_registered_model(user_app, user_model)
    assert User.objects.count() == 3
    assert Site.objects.count() == 2


@freeze_time("2012-10-15 10:00:00")
def test_deploy_datas_exclusions(caplog, db, tmp_path, settings, tests_settings):
    """
    Given excluded dump filenames should not be loaded and dump file size under the
    limit should be loaded.
    """
    caplog.set_level(logging.DEBUG)

    # Data dump samples from tests
    data_samples = tests_settings.fixtures_path / "data_samples"
    # Simulate an extracted archive with storages copied from tests samples
    archive = tmp_path / "archive"
    # Create dummy source dir where to hold data dumps
    sources = archive / "sources"
    shutil.copytree(data_samples, sources)

    blog_dump = sources / "empty-blog.json"
    blog_dump.write_text(json.dumps([], indent=4))

    # Craft a basic manifest
    manifest = {
        "version": "0.0.0-test",
        "creation": "2012-10-15T10:00:00",
        "datas": [
            Path("sources/django-site.json"),
            Path("sources/django-auth.json"),
            Path("sources/empty-blog.json"),
        ],
        "storages": []
    }

    # Deploy
    loader = Loader(logger=LoggingOutput())
    loader.deploy_datas(archive, manifest, excludes=["django-auth.json"])

    # Flatten logging messages
    logs = [
        name + ":" + str(lv) + ":" + msg
        for name, lv, msg in caplog.record_tuples
    ]

    assert logs == [
        "diskette:20:Loading data from dump 'django-site.json' (194 bytes)",
        "diskette:10:Installed 2 object(s) from 1 fixture(s)",
        "diskette:20:Ignored dump 'django-auth.json' by exclusion",
        (
            "diskette:20:Ignored dump 'empty-blog.json' because file is under the "
            "minimal size: 2 bytes"
        ),
    ]

    # Query Site and User to check expected data from dumps
    user_app, user_model = settings.AUTH_USER_MODEL.split(".")
    User = apps.get_registered_model(user_app, user_model)
    assert User.objects.count() == 0
    assert Site.objects.count() == 2
