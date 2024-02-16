import json

import pytest

from diskette.core.applications import get_appstore
from diskette.exceptions import DoesNotExistsFromAppstore

from datalookup import Node


appstore = get_appstore()


@pytest.mark.skip("Reserved to development")
def test_registry_build(tests_settings):
    """
    Build registry into a JSON file.

    WARNING: Built file is not to be commited in repository.
    """
    destination = tests_settings.application_path / "appstore.json"

    registry = appstore.as_dict()
    assert len(registry) > 0

    destination.write_text(json.dumps(registry, indent=4))
    assert destination.exists() is True


def test_normalize_label():
    """
    Method should return proper normalized model label.
    """
    assert appstore.normalize_label("Foo", app=None) == "Foo"
    assert appstore.normalize_label("Foo", app="ping") == "ping.Foo"


def test_get_app_model_labels():
    """
    Method should return all application models.
    """
    assert appstore.get_app_model_labels("auth") == [
        "auth.Permission",
        "auth.Group_permissions",
        "auth.Group",
        "auth.User_groups",
        "auth.User_user_permissions",
        "auth.User",
    ]
    assert appstore.get_app_model_labels("sites") == ["sites.Site"]


def test_get_app():
    """
    Method should properly returns the Node object for existing app or raise a
    DoesNotExistsFromAppstore error.
    """
    app = appstore.get_app("sites")
    assert isinstance(app, Node) is True
    assert app.label == "sites"

    with pytest.raises(DoesNotExistsFromAppstore) as excinfo:
        appstore.get_app("foo")

    assert str(excinfo.value) == "No app object exists for given label: 'foo'"


def test_get_model():
    """
    Method should properly returns the Node object for existing model or raise a
    DoesNotExistsFromAppstore error.
    """
    model = appstore.get_model("sites.Site")
    assert isinstance(model, Node) is True
    assert model.app == "sites"
    assert model.label == "sites.Site"

    # 'sites' is an app label so it is incorrect
    with pytest.raises(DoesNotExistsFromAppstore) as excinfo:
        appstore.get_model("sites")

    assert str(excinfo.value) == "No model object exists for given label: 'sites'"

    # There is no model with this label
    with pytest.raises(DoesNotExistsFromAppstore) as excinfo:
        appstore.get_model("foo.bar")

    assert str(excinfo.value) == "No model object exists for given label: 'foo.bar'"


def test_check_invalid_labels():
    """
    Method should returns app labels and model labels that are not valid.
    """
    assert appstore.check_invalid_labels("foo") == (['foo'], [])

    assert appstore.check_invalid_labels("plip.plop") == ([], ['plip.plop'])

    assert appstore.check_invalid_labels(["sites", "plip.plop", "foo"]) == (
        ['foo'], ['plip.plop']
    )


def test_get_all_model_labels():
    """
    Method should return a list of model labels for all enable applications.
    """
    assert appstore.get_all_model_labels() == [
        "admin.LogEntry",
        "auth.Permission",
        "auth.Group_permissions",
        "auth.Group",
        "auth.User_groups",
        "auth.User_user_permissions",
        "auth.User",
        "contenttypes.ContentType",
        "sessions.Session",
        "sites.Site",
        "djangoapp_sample.Blog",
        "djangoapp_sample.Category",
        "djangoapp_sample.Article_categories",
        "djangoapp_sample.Article",
    ]


@pytest.mark.parametrize("labels, expected", [
    # Include all model from an app
    (
        "auth",
        [
            "auth.Permission",
            "auth.Group_permissions",
            "auth.Group",
            "auth.User_groups",
            "auth.User_user_permissions",
            "auth.User",
        ],
    ),
    # Include a single model
    (
        "djangoapp_sample.Article",
        ["djangoapp_sample.Article"],
    ),
    # Include explicit models and a whole app
    (
        ["djangoapp_sample.Article", "auth.Group", "sites"],
        [
            "auth.Group",
            "sites.Site",
            "djangoapp_sample.Article",
        ],
    ),
])
def test_inclusions(labels, expected):
    """
    Model inclusions should be correctly discovered from given labels.
    """
    res = appstore.get_models_inclusions(labels)
    assert [item.label for item in res] == expected


@pytest.mark.parametrize("labels, excludes, expected", [
    # TODO: invalid label raise ValueError
    #(
        #"djangoapp_sample.foo",
        #"auth.User",
        #["djangoapp_sample.Article"],
    #),
    # Excluding a label not existing from inclusions
    (
        "djangoapp_sample.Article",
        "auth.User",
        ["djangoapp_sample.Article"],
    ),
    # Invalid exclude label does not raise error, just ignored
    (
        "djangoapp_sample.Article",
        "foo",
        ["djangoapp_sample.Article"],
    ),
    # Exclude a single model from an app
    (
        "auth",
        "auth.User",
        [
            "auth.Permission",
            "auth.Group_permissions",
            "auth.Group",
            "auth.User_groups",
            "auth.User_user_permissions",
        ],
    ),
    # Exclude a single model from different apps
    (
        ["auth", "sites"],
        "auth.User",
        [
            "auth.Permission",
            "auth.Group_permissions",
            "auth.Group",
            "auth.User_groups",
            "auth.User_user_permissions",
            "sites.Site",
        ],
    ),
    # Try to exclude a whole app over explicit label inclusions built app labels as
    # exclude labels are not supported, this lead to unexpected results (User is still
    # there)
    (
        ["auth.User", "sites"],
        ["auth"],
        ["auth.User", "sites.Site"],
    ),
    # Exclude a multiple models from different apps
    (
        [
            "auth",
            "djangoapp_sample.Blog",
            "djangoapp_sample.Article",
            "djangoapp_sample.Category",
        ],
        ["auth.User", "djangoapp_sample.Blog", "djangoapp_sample.Article"],
        [
            "auth.Permission",
            "auth.Group_permissions",
            "auth.Group",
            "auth.User_groups",
            "auth.User_user_permissions",
            "djangoapp_sample.Category",
        ],
    ),
])
def test_inclusions_with_excludes(labels, excludes, expected):
    """
    Model inclusions should be correctly discovered from given labels.
    """
    res = appstore.get_models_inclusions(labels, excludes=excludes)
    assert [item.label for item in res] == expected


@pytest.mark.parametrize("labels, expected", [
    # Implicit excludes from some omitted models on same app
    (
        "djangoapp_sample.Article",
        [
            "djangoapp_sample.Blog",
            "djangoapp_sample.Category",
            "djangoapp_sample.Article_categories",
        ],
    ),
    # Implicit excludes from some omitted models on different apps
    (
        ["djangoapp_sample.Article", "auth"],
        [
            "djangoapp_sample.Blog",
            "djangoapp_sample.Category",
            "djangoapp_sample.Article_categories",
        ],
    ),
    # Implicit excludes from some omitted models on different apps with FQM labels
    (
        ["djangoapp_sample.Article", "auth.Group"],
        [
            "auth.Permission",
            "auth.Group_permissions",
            "auth.User_groups",
            "auth.User_user_permissions",
            "auth.User",
            "djangoapp_sample.Blog",
            "djangoapp_sample.Category",
            "djangoapp_sample.Article_categories",
        ],
    ),
])
def test_exclusions_implicits(labels, expected):
    """
    Implicit model exclusions should be correctly discovered from given labels.
    """
    res = appstore.get_models_exclusions(labels)
    assert [item.label for item in res] == expected


@pytest.mark.parametrize("labels, excludes, expected", [
    # Exclude a single model from an app
    ("auth", "auth.Group", ["auth.Group"]),
    # Exclude an app
    ("auth", "sites", []),
    # Exclude a model from an app among multiple apps
    (["auth", "sites"], "auth.Group", ["auth.Group"]),
    # Exclude a model that is not implied from inclusion labels
    (
        "djangoapp_sample.Article",
        "djangoapp_sample.Blog",
        [
            "djangoapp_sample.Blog",
            "djangoapp_sample.Category",
            "djangoapp_sample.Article_categories",
        ],
    ),
    # Exclude a whole app after inclusion on specific models, exclusion primes on
    # inclusion
    (
        ["djangoapp_sample.Article", "auth.Group"],
        None,
        [
            "auth.Permission",
            "auth.Group_permissions",
            "auth.User_groups",
            "auth.User_user_permissions",
            "auth.User",
            "djangoapp_sample.Blog",
            "djangoapp_sample.Category",
            "djangoapp_sample.Article_categories",
        ],
    ),
])
def test_exclusions_explicits(labels, excludes, expected):
    """
    Both explicit and implicit model exclusions should be correctly discovered from
    given labels and excludes.
    """
    res = appstore.get_models_exclusions(labels, excludes=excludes)
    assert [item.label for item in res] == expected
