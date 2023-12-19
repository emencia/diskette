import json

import pytest
from freezegun import freeze_time


from diskette.dump.manager import DumpManager
from diskette.exceptions import DumpManagerError
from diskette.utils.factories import UserFactory


# None of these definitions are for existing app or models, these are just dummy samples
SAMPLE_APPS = [
    ("foo.bar", {
        "models": "bar",
    }),

    ("bang", {
        "natural_foreign": True,
        "natural_primary": True,
        "models": "bang",
    }),

    ("ZipZapZop", {
        "models": ["zip.zap", "zip.zop"],
        "exclude": ["zip.zop"],
    }),

    ("ping-pong", {
        "comments": "Lorem ipsum",
        "natural_foreign": True,
        "natural_primary": True,
        "models": ["ping"],
        "filename": "ping_pong.json",
        "exclude": ["ping.nope"],
    }),
]


def test_manager_invalid_duplicate():
    """
    An error should be raised when given application list have duplicate names.
    """
    with pytest.raises(DumpManagerError) as excinfo:
        DumpManager([
            ("bang", {"models": "bang"}),
            ("foo.bar", {"models": "bar"}),
            ("foo.bar", {"models": "bar"}),
            ("ping", {"models": "ping"}),
            ("pong", {"models": "pong"}),
            ("bang", {"models": "bangbang"}),
        ])

    assert str(excinfo.value) == (
        "There was some duplicate names from applications: foo.bar, bang"
    )


def test_manager_payload():
    """
    Manager should return a normalized payload for applications
    """
    manager = DumpManager(SAMPLE_APPS)
    assert manager.export_as_payload() == [
        {
            "models": [
                "bar"
            ],
            "exclude": [],
            "natural_foreign": False,
            "natural_primary": False,
            "filename": "foobar.json",
        },
        {
            "models": [
                "bang"
            ],
            "exclude": [],
            "natural_foreign": True,
            "natural_primary": True,
            "filename": "bang.json",
        },
        {
            "models": [
                "zip.zap",
                "zip.zop"
            ],
            "exclude": [
                "zip.zop"
            ],
            "natural_foreign": False,
            "natural_primary": False,
            "filename": "zipzapzop.json",
        },
        {
            "models": [
                "ping"
            ],
            "exclude": [
                "ping.nope"
            ],
            "natural_foreign": True,
            "natural_primary": True,
            "filename": "ping_pong.json",
        }
    ]

    # Simple check with enabled 'named' and 'commented' options
    manager = DumpManager([
        ("foo.bar", {"models": "bar"}),
    ])
    assert manager.export_as_payload(named=True, commented=True) == [
        {
            "name": "foo.bar",
            "models": [
                "bar"
            ],
            "exclude": [],
            "natural_foreign": False,
            "natural_primary": False,
            "filename": "foobar.json",
            "comments": None
        }
    ]


def test_manager_commands(tmp_path):
    """
    Manager should correctly build command line for each app.
    """
    manager = DumpManager(
        [("foo.bar", {"models": "bar"})], executable="/bin/foo",
    )
    assert manager.export_as_commands() == [
        ("foo.bar", "/bin/foo dumpdata bar"),
    ]
    assert manager.export_as_commands(indent=2, destination=tmp_path) == [
        (
            "foo.bar",
            "/bin/foo dumpdata --indent=2 bar --output={}/{}".format(
                tmp_path,
                "foobar.json"
            )
        ),
    ]

    manager = DumpManager(SAMPLE_APPS)
    # print(json.dumps(manager.export_as_commands(), indent=4))
    assert manager.export_as_commands() == [
        ("foo.bar", "dumpdata bar"),
        ("bang", "dumpdata bang --natural-foreign --natural-primary"),
        ("ZipZapZop", "dumpdata zip.zap zip.zop --exclude zip.zop"),
        (
            "ping-pong",
            (
                "dumpdata ping --natural-foreign --natural-primary "
                "--exclude ping.nope"
            )
        ),
    ]


@freeze_time("2012-10-15 10:00:00")
def test_manager_calls(db, tmp_path):
    """
    Manager should calls dumpdata command and return their correct outputs.
    """
    picsou = UserFactory()
    donald = UserFactory()
    # Force a dummy string password easier to assert
    picsou.password = "dummy"
    picsou.save()
    donald.password = "dummy"
    donald.save()

    manager = DumpManager([
        ("Django auth", {"models": ["auth.group", "auth.user"]}),
        ("Django site", {"models": ["sites"]}),
    ])
    results = manager.export_with_calls()
    deserialized = [
        (k, json.loads(v))
        for k, v in results
    ]
    # print(json.dumps(deserialized, indent=4))
    assert deserialized == [
        (
            "Django auth",
            [
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
                },
                {
                    "model": "auth.user",
                    "pk": donald.id,
                    "fields": {
                        "password": "dummy",
                        "last_login": None,
                        "is_superuser": False,
                        "username": donald.username,
                        "first_name": donald.first_name,
                        "last_name": donald.last_name,
                        "email": donald.email,
                        "is_staff": False,
                        "is_active": True,
                        "date_joined": "2012-10-15T10:00:00Z",
                        "groups": [],
                        "user_permissions": []
                    }
                },
            ]
        ),
        (
            "Django site",
            [
                {
                    "model": "sites.site",
                    "pk": 1,
                    "fields": {
                        "domain": "example.com",
                        "name": "example.com"
                    }
                }
            ]
        ),
    ]


@freeze_time("2012-10-15 10:00:00")
def test_manager_calls_destination(db, tmp_path):
    """
    With a given destination the manager should calls dumpdata command and return
    dump filepaths.
    """
    picsou = UserFactory()
    donald = UserFactory()
    # Force a dummy string password easier to assert
    picsou.password = "dummy"
    picsou.save()
    donald.password = "dummy"
    donald.save()

    manager = DumpManager([
        ("Django auth", {"models": ["auth.group", "auth.user"]}),
        ("Django site", {"models": ["sites"]}),
    ])
    results = manager.export_with_calls(destination=tmp_path)

    expected_auth_dump_path = tmp_path / "django-auth.json"
    expected_site_dump_path = tmp_path / "django-site.json"
    deserialized = [
        (k, json.loads(v))
        for k, v in results
    ]
    assert deserialized == [
        ("Django auth", {"destination": str(expected_auth_dump_path)}),
        ("Django site", {"destination": str(expected_site_dump_path)}),
    ]

    assert expected_auth_dump_path.exists() is True
    assert expected_site_dump_path.exists() is True

    # Check written dumps contents
    assert json.loads(expected_auth_dump_path.read_text()) == [
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
        },
        {
            "model": "auth.user",
            "pk": donald.id,
            "fields": {
                "password": "dummy",
                "last_login": None,
                "is_superuser": False,
                "username": donald.username,
                "first_name": donald.first_name,
                "last_name": donald.last_name,
                "email": donald.email,
                "is_staff": False,
                "is_active": True,
                "date_joined": "2012-10-15T10:00:00Z",
                "groups": [],
                "user_permissions": []
            }
        },
    ]

    assert json.loads(expected_site_dump_path.read_text()) == [
        {
            "model": "sites.site",
            "pk": 1,
            "fields": {
                "domain": "example.com",
                "name": "example.com"
            }
        }
    ]
