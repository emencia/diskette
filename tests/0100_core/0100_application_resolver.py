import pytest

from diskette.exceptions import ApplicationConfigError, AppModelResolverError
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


@pytest.mark.parametrize("labels, excludes, expected", [
    # A single fully qualified label
    ("auth.group", [], ["auth.group"]),
    # This demonstrates that fully qualified label (app+model) are not resolved and a
    # label for a non existing app or model can be given without error at this level.
    ("nope.foo", None, ["nope.foo"]),
    # A set of fully qualified labels
    (["auth.group", "auth.user"], None, ["auth.group", "auth.user"]),
    # Resulting list may be empty, this upper level code that need to manage this case
    ("auth.group", ["auth.group"], []),
    # Exclude filter is case sensitive
    (
        ["auth.group", "auth.user"],
        ["auth.group", "auth.User"],
        ["auth.user"],
    ),
    # A single app label resolved to fully qualified model labels
    (
        "djangoapp_sample",
        None,
        [
            "djangoapp_sample.Blog",
            "djangoapp_sample.Category",
            "djangoapp_sample.Article_categories",
            "djangoapp_sample.Article",
        ],
    ),
    # A mix of fully qualified and app labels
    (
        ["auth.group", "djangoapp_sample", "sites"],
        None,
        [
            "auth.group",
            "djangoapp_sample.Blog",
            "djangoapp_sample.Category",
            "djangoapp_sample.Article_categories",
            "djangoapp_sample.Article",
            "sites.Site"
        ],
    ),
    # Mixed label with some excludes
    (
        ["auth", "djangoapp_sample", "sites"],
        ["auth.Group", "djangoapp_sample.Article"],
        [
            "auth.Permission",
            "auth.Group_permissions",
            "auth.User_groups",
            "auth.User_user_permissions",
            "auth.User",
            "djangoapp_sample.Blog",
            "djangoapp_sample.Category",
            "djangoapp_sample.Article_categories",
            "sites.Site"
        ],
    ),
])
def test_resolve_names_valid(labels, excludes, expected):
    """
    Method should resolve the proper model labels from given contents.
    """
    resolver = AppModelResolverAbstract()

    assert resolver.resolve_labels(labels, excludes=excludes) == expected


def test_resolve_names_invalid():
    """
    Method should raise an exception in some expected cases.
    """
    resolver = AppModelResolverAbstract()

    with pytest.raises(LookupError) as excinfo:
        resolver.resolve_labels("foo")

    assert str(excinfo.value) == (
        "No installed app with label 'foo'."
    )

    with pytest.raises(AppModelResolverError) as excinfo:
        resolver.resolve_labels(".group")

    assert str(excinfo.value) == (
        "Label includes a dot without leading application name: .group"
    )
