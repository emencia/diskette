import json

import pytest
from freezegun import freeze_time

from django.core.management.base import CommandError

from diskette.dump.models import ApplicationModel
from diskette.dump.serializers import DjangoDumpDataSerializer
from diskette.utils.factories import UserFactory


@freeze_time("2012-10-15 10:00:00")
def test_serializer_command(db, tmp_path):
    """
    Serializer should correctly call the dumpdata command that will return JSON for
    application datas.
    """
    serializer = DjangoDumpDataSerializer()

    # With a non existing model
    app_foo = ApplicationModel("foo.bar", ["bar"])
    assert serializer.command(app_foo) == "dumpdata bar"


@freeze_time("2012-10-15 10:00:00")
def test_serializer_call(db, tmp_path):
    """
    Serializer should correctly call the dumpdata command that will return JSON for
    application datas.
    """
    serializer = DjangoDumpDataSerializer()

    # With a non existing model
    app_foo = ApplicationModel("foo.bar", ["bar"])
    with pytest.raises(CommandError) as excinfo:
        serializer.call(app_foo)

    assert str(excinfo.value) == "No installed app with label 'bar'."

    # With existing model from Django contrib.auth
    picsou = UserFactory()
    # Force a dummy string password easier to assert
    picsou.password = "dummy"
    picsou.save()

    app_auth = ApplicationModel("Django auth", ["auth.group", "auth.user"])
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
