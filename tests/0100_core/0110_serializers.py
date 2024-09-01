import json
import logging

from freezegun import freeze_time

from diskette.core.applications import ApplicationConfig
from diskette.core.serializers import DumpdataSerializer, LoaddataSerializer
from diskette.factories import UserFactory
from diskette.utils.loggers import LoggingOutput


@freeze_time("2012-10-15 10:00:00")
def test_dump_command(db, tmp_path):
    """
    Serializer should correctly build the dumpdata command that will return JSON for
    application datas.

    .. Note::
        The test is pretty basic and does not care (yet) of command options.
    """
    serializer = DumpdataSerializer()

    app_foo = ApplicationConfig("Site objects", ["sites"])
    assert serializer.command(app_foo) == "dumpdata sites.Site"


@freeze_time("2012-10-15 10:00:00")
def test_dump_call(db, tmp_path):
    """
    Serializer should correctly call the dumpdata command to return JSON for
    application datas.
    """
    serializer = DumpdataSerializer()

    picsou = UserFactory()
    # Force a dummy string password easier to assert
    picsou.password = "dummy"
    picsou.save()

    app_auth = ApplicationConfig("Django auth", ["auth.Group", "auth.User"])
    results = serializer.call(app_auth)
    deserialized = json.loads(results)
    assert deserialized == [
        {
            "model": "auth.user",
            "pk": picsou.id,
            "fields": {
                "password": "dummy",
                "last_login": None,
                "is_superuser": False,
                "username": picsou.username,
                "first_name": picsou.first_name,
                "last_name": picsou.last_name,
                "email": picsou.email,
                "is_staff": False,
                "is_active": True,
                "date_joined": "2012-10-15T10:00:00Z",
                "groups": [],
                "user_permissions": []
            }
        }
    ]


@freeze_time("2012-10-15 10:00:00")
def test_load_call(caplog, db, tests_settings, tmp_path):
    """
    Serializer should correctly call the loaddata command to load JSON for
    application datas.

    .. Note::
        The test is pretty basic and does not care (yet) of command options.
    """
    caplog.set_level(logging.DEBUG)

    data_samples = tests_settings.fixtures_path / "data_samples"

    serializer = LoaddataSerializer(logger=LoggingOutput())

    assert serializer.call(data_samples / "django-site.json") == (
        "Installed 2 object(s) from 1 fixture(s)"
    )


@freeze_time("2012-10-15 10:00:00")
def test_load_command(db, tests_settings, tmp_path):
    """
    Serializer should correctly build the loaddata command to load JSON for
    application datas.
    """
    data_samples = tests_settings.fixtures_path / "data_samples"

    serializer = LoaddataSerializer()

    dump = data_samples / "django-site.json"

    # Without any option
    assert serializer.command(dump) == (
        "loaddata {}/django-site.json".format(data_samples)
    )

    # Without some options
    command = serializer.command(dump, ignorenonexistent=True, excludes=["foo", "bar"])
    assert command == (
        "loaddata {}/django-site.json --ignorenonexistent --exclude foo --exclude bar"
    ).format(data_samples)


@freeze_time("2012-10-15 10:00:00")
def test_load_command_false_option(db, tests_settings, tmp_path):
    """
    Since programmatically called, a flag option with a false value is not correctly
    ignored from the command.
    """
    data_samples = tests_settings.fixtures_path / "data_samples"

    serializer = LoaddataSerializer()

    dump = data_samples / "django-site.json"

    # Without any option
    assert serializer.command(dump) == (
        "loaddata {}/django-site.json".format(data_samples)
    )

    # Without some options
    command = serializer.command(dump, ignorenonexistent=False, excludes=["foo", "bar"])
    assert command == (
        "loaddata {}/django-site.json --exclude foo --exclude bar"
    ).format(data_samples)
