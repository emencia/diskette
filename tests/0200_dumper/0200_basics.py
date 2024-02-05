import json
import shutil

import pytest
from freezegun import freeze_time

from diskette.core.dumper import Dumper
from diskette.exceptions import DumperError, ApplicationRegistryError


def test_validate_applications():
    """
    Application validation should raise an ApplicationRegistryError exception that
    contains detail messages for model errors.
    """
    manager = Dumper([
        ("meh", {}),
        ("foo.bar", {"models": "bar", "excludes": "nope"}),
    ])
    with pytest.raises(ApplicationRegistryError) as excinfo:
        manager.validate_applications()

    assert str(excinfo.value) == (
        "Some defined applications have errors: meh, foo.bar"
    )
    assert excinfo.value.get_payload_details() == [
        "<ApplicationConfig: meh>: 'models' must not be an empty value.",
        "<ApplicationConfig: foo.bar>: 'excludes' argument must be a list.",
    ]


def test_invalid_duplicate():
    """
    An error should be raised when given application list have duplicate names.
    """
    with pytest.raises(DumperError) as excinfo:
        Dumper([
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


def test_exported_dicts():
    """
    Manager should return a normalized dict for application options or payload.
    """
    manager = Dumper([
        (
            "django.contrib.sites", {
                "comments": "django.contrib.sites",
                "natural_foreign": True,
                "models": "sites"
            }
        ),
        (
            "django.contrib.auth", {
                "comments": "django.contrib.auth: user and groups, no perms",
                "natural_foreign": True,
                "models": ["auth.group","auth.user"]
            }
        ),
        (
            "blog", {
                "comments": "internal blog sample app",
                "models": "djangoapp_sample",
                "excludes": ["blog.category"],
                "comments": "Lorem ipsum",
                "natural_foreign": False,
                "natural_primary": True,
                "filename": "blog.json",
                "allow_drain": True,
            }
        ),
    ])

    assert manager.dump_options() == [
        {
            "models": ["sites.Site"],
            "excludes": [],
            "natural_foreign": True,
            "natural_primary": False,
            "filename": "djangocontribsites.json"
        },
        {
            "models": ["auth.group", "auth.user"],
            "excludes": [],
            "natural_foreign": True,
            "natural_primary": False,
            "filename": "djangocontribauth.json"
        },
        {
            "models": [
                "djangoapp_sample.Blog",
                "djangoapp_sample.Category",
                "djangoapp_sample.Article_categories",
                "djangoapp_sample.Article"
            ],
            "excludes": ["blog.category"],
            "natural_foreign": False,
            "natural_primary": True,
            "filename": "blog.json"
        }
    ]

    assert manager.payload() == [
        {
            "name": "django.contrib.sites",
            "models": ["sites.Site"],
            "excludes": [],
            "natural_foreign": True,
            "natural_primary": False,
            "comments": "django.contrib.sites",
            "filename": "djangocontribsites.json",
            "is_drain": False,
            "allow_drain": False
        },
        {
            "name": "django.contrib.auth",
            "models": ["auth.group", "auth.user"],
            "excludes": [],
            "natural_foreign": True,
            "natural_primary": False,
            "comments": "django.contrib.auth: user and groups, no perms",
            "filename": "djangocontribauth.json",
            "is_drain": False,
            "allow_drain": False
        },
        {
            "name": "blog",
            "models": [
                "djangoapp_sample.Blog",
                "djangoapp_sample.Category",
                "djangoapp_sample.Article_categories",
                "djangoapp_sample.Article"
            ],
            "excludes": ["blog.category"],
            "natural_foreign": False,
            "natural_primary": True,
            "comments": "Lorem ipsum",
            "filename": "blog.json",
            "is_drain": False,
            "allow_drain": True
        }
    ]


@pytest.mark.skip("Refactoring drainage, resolver and excludes, Part 1")
def test_get_involved_models_sample_apps():
    """
    Method should returns the list of involved models from application definitions,
    optionally with the excluded ones.
    """
    # Only processed models (without exludes)
    manager = Dumper([
        ("bang", {
            "models": "bang",
            "excludes": [],
            "allow_drain": True,
        }),
        ("foo", {
            "models": "bar",
            "excludes": ["zip"],
            "allow_drain": True,
        }),
        ("ping", {
            "models": "ping",
            "excludes": ["pong", "pung"],
        }),
    ])
    print()
    print(manager.get_involved_models())
    print()
    assert manager.get_involved_models() == [
        "bang",
        "bar",
        "ping"
    ]

    assert 1 == 42


@freeze_time("2012-10-15 10:00:00")
def test_build_dump_manifest(manifest_version, tmp_path, tests_settings):
    """
    Dump manifest should contains every dumped files, archived storages and some
    context informations. Data dump list should respect order of applications.
    """
    # Make storages samples
    storage_samples = tests_settings.fixtures_path / "storage_samples"
    storage_tmp = tmp_path / "storages"
    storage_tmp.mkdir(parents=True)
    storage_1 = storage_tmp / "storage-1"
    storage_2 = storage_tmp / "storage-2"
    shutil.copytree(storage_samples / "storage-1", storage_1)
    shutil.copytree(storage_samples / "storage-2", storage_2)

    # Make data samples
    data_tmp = tmp_path / "data"
    data_tmp.mkdir(parents=True)
    foobar_data_dump = data_tmp / "foo-bar.json"
    foobar_data_dump.write_text("{\"dummy\": True}")
    users_data_dump = data_tmp / "users.json"
    users_data_dump.write_text("{\"dummy\": True}")

    # Configure manager
    manager = Dumper(
        [
            ("users", {"models": ["author.user"], "filename": "users.json"}),
            ("foo.bar", {"models": "bar", "filename": "foo-bar.json"}),
        ],
        storages_basepath=tmp_path,
        storages=[
            storage_1,
            storage_2
        ]
    )

    manifest_path = manager.build_dump_manifest(
        tmp_path,
        data_tmp,
        with_data=True,
        with_storages=True
    )
    manifest = json.loads(manifest_path.read_text())

    assert manifest == {
        "version": "0.0.0-test",
        "creation": "2012-10-15T10:00:00",
        "datas": [
            "data/users.json",
            "data/foo-bar.json"
        ],
        "storages": [
            "storages/storage-1",
            "storages/storage-2"
        ]
    }