import pytest

from diskette.dump.models import ApplicationModel
from diskette.exceptions import ApplicationModelError


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


def test_application_invalid_exclude():
    """
    Application should raise an error from invalid 'exclude' type.
    """
    app = ApplicationModel("foo.bar", ["bar"], exclude="nope")
    with pytest.raises(ApplicationModelError) as excinfo:
        app.validate()

    assert str(excinfo.value) == (
        "<ApplicationModel: foo.bar>: 'exclude' argument must be a list."
    )


def test_application_invalid_format():
    """
    Application should raise an error from invalid 'filename' extension.
    """
    # Empty file extension
    app = ApplicationModel("foo.bar", ["bar"], filename="nope")
    with pytest.raises(ApplicationModelError) as excinfo:
        app.validate()
    assert str(excinfo.value) == (
        "<ApplicationModel: foo.bar>: Given file name 'nope' must have a file "
        "extension to discover format."
    )

    # Non allowed file extension
    app = ApplicationModel("foo.bar", ["bar"], filename="nope.txt")
    with pytest.raises(ApplicationModelError) as excinfo:
        app.validate()

    assert str(excinfo.value) == (
        "<ApplicationModel: foo.bar>: Given file name 'nope.txt' must use a file "
        "extension from allowed formats: json, jsonl, xml, yaml"
    )


def test_application_valid():
    """
    With correct values, Application object should be correctly created.
    """
    # Basic with required arguments
    app_foo = ApplicationModel("foo.bar", ["bar"])
    assert repr(app_foo) == "<ApplicationModel: foo.bar>"
    assert app_foo.as_dict() == {
        "models": [
            "bar"
        ],
        "exclude": [],
        "natural_foreign": False,
        "natural_primary": False,
        "filename": "foobar.json",
    }

    # Fullfill every arguments
    app_ping = ApplicationModel(
        "Ping",
        ["ping"],
        comments="Lorem ipsum",
        natural_foreign=True,
        natural_primary=True,
        exclude=["ping.nope"],
        filename="ping_pong.json",
    )
    assert repr(app_ping) == "<ApplicationModel: Ping>"
    assert app_ping.as_dict() == {
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
