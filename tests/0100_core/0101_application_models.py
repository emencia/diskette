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


def test_application_empty_models():
    """
    Application should raise an error when 'models' is empty.
    """
    app = ApplicationConfig("foo.bar")
    with pytest.raises(ApplicationConfigError) as excinfo:
        app.validate()

    assert str(excinfo.value) == (
        "<ApplicationConfig: foo.bar>: 'models' must not be an empty value."
    )


def test_application_invalid_models():
    """
    Application should raise an error when 'models' is an invalid application label.
    """
    app = ApplicationConfig("foo", models="bar")
    with pytest.raises(LookupError) as excinfo:
        app.validate()

    assert str(excinfo.value) == "No installed app with label 'bar'."


def test_application_invalid_format():
    """
    Application should raise an error from invalid 'filename' extension.
    """
    # Empty file extension
    app = ApplicationConfig("sites", models=["sites"], filename="nope")
    with pytest.raises(ApplicationConfigError) as excinfo:
        app.validate()
    assert str(excinfo.value) == (
        "<ApplicationConfig: sites>: Given file name 'nope' must have a file "
        "extension to discover format."
    )

    # Non allowed file extension
    app = ApplicationConfig("sites", models=["sites"], filename="nope.txt")
    with pytest.raises(ApplicationConfigError) as excinfo:
        app.validate()

    assert str(excinfo.value) == (
        "<ApplicationConfig: sites>: Given file name 'nope.txt' must use a file "
        "extension from allowed formats: json, jsonl, xml, yaml"
    )


def test_application_valid_basic():
    """
    With minimal correct values, Application object should be correctly created.
    """
    app_foo = ApplicationConfig("Site objects", models=["sites"])
    assert repr(app_foo) == "<ApplicationConfig: Site objects>"
    assert app_foo.as_config() == {
        "name": "Site objects",
        "comments": None,
        "is_drain": False,
        "allow_drain": False,
        "models": ["sites.Site"],
        "excludes": [],
        "natural_foreign": False,
        "natural_primary": False,
        "filename": "site-objects.json",
    }
    assert app_foo.as_options() == {
        "models": ["sites.Site"],
        "excludes": [],
        "natural_foreign": False,
        "natural_primary": False,
        "filename": "site-objects.json",
    }


def test_application_valid_full():
    """
    With all correct values, Application object should be correctly created.
    """
    app_ping = ApplicationConfig(
        "Django auth",
        models=["auth"],
        comments="Lorem ipsum",
        natural_foreign=True,
        natural_primary=True,
        excludes=["ping.nope"],
        filename="ping_pong.json",
        allow_drain=True,
    )
    assert repr(app_ping) == "<ApplicationConfig: Django auth>"
    assert app_ping.as_config() == {
        "name": "Django auth",
        "comments": "Lorem ipsum",
        "is_drain": False,
        "allow_drain": True,
        "models": [
            "auth.Permission",
            "auth.Group_permissions",
            "auth.Group",
            "auth.User_groups",
            "auth.User_user_permissions",
            "auth.User",
        ],
        "excludes": ["ping.nope"],
        "natural_foreign": True,
        "natural_primary": True,
        "filename": "ping_pong.json",
    }
    assert app_ping.as_options() == {
        "models": [
            "auth.Permission",
            "auth.Group_permissions",
            "auth.Group",
            "auth.User_groups",
            "auth.User_user_permissions",
            "auth.User",
        ],
        "excludes": ["ping.nope"],
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
