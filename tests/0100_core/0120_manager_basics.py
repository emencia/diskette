import json
import shutil

import pytest
from freezegun import freeze_time

from diskette.core.manager import DumpManager
from diskette.exceptions import DumpManagerError, ApplicationRegistryError

from tests.samples import SAMPLE_APPS


def test_validate_applications():
    """
    Application validation should raise an ApplicationRegistryError exception that
    contains detail messages for model errors.
    """
    manager = DumpManager([
        ("meh", {}),
        ("foo.bar", {"models": "bar", "excludes": "nope"}),
    ])
    with pytest.raises(ApplicationRegistryError) as excinfo:
        manager.validate_applications()

    assert str(excinfo.value) == (
        "Some defined applications have errors: meh, foo.bar"
    )
    assert excinfo.value.get_payload_details() == [
        "<ApplicationModel: meh>: 'models' must not be an empty value.",
        "<ApplicationModel: foo.bar>: 'excludes' argument must be a list.",
    ]


def test_invalid_duplicate():
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


def test_payload():
    """
    Manager should return a normalized dict for application options or payload.
    """
    manager = DumpManager(SAMPLE_APPS)
    assert manager.dump_options() == [
        {
            "models": [
                "blog"
            ],
            "excludes": [],
            "natural_foreign": False,
            "natural_primary": False,
            "filename": "blog.json",
        },
        {
            "models": [
                "tags"
            ],
            "excludes": [],
            "natural_foreign": True,
            "natural_primary": True,
            "filename": "tags.json",
        },
        {
            "models": [
                "authors.user",
                "authors.pin"
            ],
            "excludes": [
                "authors.pin"
            ],
            "natural_foreign": False,
            "natural_primary": False,
            "filename": "authors.json",
        },
        {
            "models": [
                "contacts"
            ],
            "excludes": [
                "contacts.token"
            ],
            "natural_foreign": False,
            "natural_primary": False,
            "filename": "contacts.json",
        },
        {
            "models": [
                "cart.item",
                "cart.payment"
            ],
            "excludes": [
                "cart.payment"
            ],
            "natural_foreign": False,
            "natural_primary": False,
            "filename": "cart.json",
        },
        {
            "models": [
                "pages"
            ],
            "excludes": [
                "pages.revision"
            ],
            "natural_foreign": True,
            "natural_primary": True,
            "filename": "cmspages.json",
        }
    ]

    # Simple check with enabled 'named' and 'commented' options
    manager = DumpManager([
        ("foo.bar", {"models": "bar"}),
    ])
    assert manager.payload() == [
        {
            "name": "foo.bar",
            "comments": None,
            "allow_drain": False,
            "is_drain": False,
            "models": [
                "bar"
            ],
            "excludes": [],
            "natural_foreign": False,
            "natural_primary": False,
            "filename": "foobar.json",
        }
    ]


def test_get_involved_models():
    """
    Method should returns the list of involved models from application definitions,
    optionally with the excluded ones.
    """
    # Only processed models (without exludes)
    manager = DumpManager(SAMPLE_APPS)
    assert manager.get_involved_models(with_excluded=False) == [
        "blog",
        "tags",
        "authors.user",
        "authors.pin",
        "contacts",
        "cart.item",
        "cart.payment",
        "pages",
    ]

    # Processed models and their excluded ones
    manager = DumpManager(SAMPLE_APPS)
    # print()
    # print(json.dumps(manager.get_involved_models(with_excluded=True), indent=4))
    # print()
    assert manager.get_involved_models(with_excluded=True) == [
        "blog",
        "tags",
        "authors.user",
        "authors.pin",
        "contacts",
        "cart.item",
        "cart.payment",
        "pages",
        "pages.revision",
    ]


@freeze_time("2012-10-15 10:00:00")
def test_build_dump_manifest(manifest_version, tmp_path, tests_settings):
    """
    Dump manifest should contains every dumped files, archived storages and some
    context informations.
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
    dummy_data_dump = data_tmp / "foo.json"
    dummy_data_dump.write_text("{\"dummy\": True}")

    # Configure manager
    manager = DumpManager(
        [],
        basepath=tmp_path,
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
            "data/foo.json"
        ],
        "storages": [
            "storages/storage-1",
            "storages/storage-2"
        ]
    }
