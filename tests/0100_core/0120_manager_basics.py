import pytest

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
