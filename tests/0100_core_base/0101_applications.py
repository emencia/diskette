import pytest

from diskette.core.applications import ApplicationConfig, DrainApplicationConfig
from diskette.exceptions import ApplicationConfigError


def test_application_invalid_excludes():
    """
    Application should raise an error from invalid 'excludes' type.
    """
    app = ApplicationConfig("foo.bar", models=["bar"], excludes="nope")
    with pytest.raises(ApplicationConfigError) as excinfo:
        app.validate()

    assert str(excinfo.value) == (
        "<ApplicationConfig: foo.bar>: 'excludes' argument must be a list."
    )


def test_application_invalid_models():
    """
    Application should raise an error when 'models' is empty.
    """
    app = ApplicationConfig("foo.bar")
    with pytest.raises(ApplicationConfigError) as excinfo:
        app.validate()

    assert str(excinfo.value) == (
        "<ApplicationConfig: foo.bar>: 'models' must not be an empty value."
    )


def test_application_invalid_format():
    """
    Application should raise an error from invalid 'filename' extension.
    """
    # Empty file extension
    app = ApplicationConfig("foo.bar", models=["bar"], filename="nope")
    with pytest.raises(ApplicationConfigError) as excinfo:
        app.validate()
    assert str(excinfo.value) == (
        "<ApplicationConfig: foo.bar>: Given file name 'nope' must have a file "
        "extension to discover format."
    )

    # Non allowed file extension
    app = ApplicationConfig("foo.bar", models=["bar"], filename="nope.txt")
    with pytest.raises(ApplicationConfigError) as excinfo:
        app.validate()

    assert str(excinfo.value) == (
        "<ApplicationConfig: foo.bar>: Given file name 'nope.txt' must use a file "
        "extension from allowed formats: json, jsonl, xml, yaml"
    )


def test_application_valid():
    """
    With correct values, Application object should be correctly created.
    """
    # Basic with required arguments
    app_foo = ApplicationConfig("foo.bar", models=["bar"])
    assert repr(app_foo) == "<ApplicationConfig: foo.bar>"
    assert app_foo.as_config() == {
        "name": "foo.bar",
        "comments": None,
        "is_drain": False,
        "allow_drain": False,
        "models": [
            "bar"
        ],
        "excludes": [],
        "natural_foreign": False,
        "natural_primary": False,
        "filename": "foobar.json",
    }
    assert app_foo.as_options() == {
        "models": [
            "bar"
        ],
        "excludes": [],
        "natural_foreign": False,
        "natural_primary": False,
        "filename": "foobar.json",
    }

    # Fullfill every arguments
    app_ping = ApplicationConfig(
        "Ping",
        models=["ping"],
        comments="Lorem ipsum",
        natural_foreign=True,
        natural_primary=True,
        excludes=["ping.nope"],
        filename="ping_pong.json",
    )
    assert repr(app_ping) == "<ApplicationConfig: Ping>"
    assert app_ping.as_config() == {
        "name": "Ping",
        "comments": "Lorem ipsum",
        "is_drain": False,
        "allow_drain": False,
        "models": [
            "ping"
        ],
        "excludes": [
            "ping.nope"
        ],
        "natural_foreign": True,
        "natural_primary": True,
        "filename": "ping_pong.json",
    }
    assert app_ping.as_options() == {
        "models": [
            "ping"
        ],
        "excludes": [
            "ping.nope"
        ],
        "natural_foreign": True,
        "natural_primary": True,
        "filename": "ping_pong.json",
    }


def test_drain_empty_models():
    """
    Drain application does not require 'models' argument.
    """
    app = DrainApplicationConfig("foo.bar")
    app.validate()

    assert app.models == []


def test_drain_payload():
    """
    Drain application should have some different items in its payload.
    """
    app = DrainApplicationConfig("foo.bar")
    app.validate()

    assert app.as_config() == {
        "name": "foo.bar",
        "comments": None,
        "is_drain": True,
        "drain_excluded": False,
        "models": [],
        "excludes": [],
        "natural_foreign": False,
        "natural_primary": False,
        "filename": "foobar.json",
    }
    assert app.as_options() == {
        "models": [],
        "excludes": [],
        "natural_foreign": False,
        "natural_primary": False,
        "filename": "foobar.json",
    }
