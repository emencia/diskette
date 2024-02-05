import pytest

from diskette.exceptions import AppModelResolverError
from diskette.core.applications import AppModelResolverAbstract


def test_normalize_model_name():
    """
    Method should return proper normalized model label.
    """
    resolver = AppModelResolverAbstract()

    assert resolver.normalize_model_name("Foo", app=None) == "Foo"
    assert resolver.normalize_model_name("Foo", app="ping") == "ping.Foo"


def test_get_all_models():
    """
    Method should return a list of model labels for all enable applications.
    """
    resolver = AppModelResolverAbstract()

    assert resolver.get_all_models() == [
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
    # A single app label
    (
        "djangoapp_sample",
        [
            "djangoapp_sample.Blog",
            "djangoapp_sample.Category",
            "djangoapp_sample.Article_categories",
            "djangoapp_sample.Article",
        ],
    ),
    # A single full label
    (
        "auth.group",
        ["auth.group"],
    ),
    # A set of full labels
    (
        ["auth.group", "auth.user"],
        ["auth.group", "auth.user"],
    ),
    # A mix of full label and app labels only
    (
        ["auth.group", "djangoapp_sample", "sites"],
        [
            "auth.group",
            "djangoapp_sample.Blog",
            "djangoapp_sample.Category",
            "djangoapp_sample.Article_categories",
            "djangoapp_sample.Article",
            "sites.Site"
        ],
    ),
    # This show that full label (app+model) are not resolved and a label for a non
    # existing app or model can be given without error at this level.
    (
        "auth.group",
        ["auth.group"],
    ),
])
def test_resolve_names_valid(labels, expected):
    """
    Method should resolve the proper model labels from given contents.
    """
    resolver = AppModelResolverAbstract()

    assert resolver.get_label_model_names(labels) == expected


def test_resolve_names_invalid():
    """
    Method should raise an exception in some expected cases.
    """
    resolver = AppModelResolverAbstract()

    with pytest.raises(LookupError) as excinfo:
        resolver.get_label_model_names("foo")

    assert str(excinfo.value) == (
        "No installed app with label 'foo'."
    )

    with pytest.raises(AppModelResolverError) as excinfo:
        resolver.get_label_model_names(".group")

    assert str(excinfo.value) == (
        "Label includes a dot without leading application name: .group"
    )
