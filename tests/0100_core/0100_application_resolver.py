import pytest

from diskette.exceptions import ApplicationConfigError, AppModelResolverError
from diskette.core.applications import AppModelResolverAbstract


@pytest.mark.skip("DEPRECATED")
def test_normalize_model_name():
    """
    Method should return proper normalized model label.

    DEPRECATED: Ported to store tests
    """
    resolver = AppModelResolverAbstract()

    assert resolver.normalize_model_name("Foo", app=None) == "Foo"
    assert resolver.normalize_model_name("Foo", app="ping") == "ping.Foo"


@pytest.mark.skip("DEPRECATED")
def test_get_app_models():
    """
    Method should return all application models.

    DEPRECATED: Ported to store tests
    """
    resolver = AppModelResolverAbstract()

    assert resolver.get_app_models("auth") == [
        "auth.Permission",
        "auth.Group_permissions",
        "auth.Group",
        "auth.User_groups",
        "auth.User_user_permissions",
        "auth.User",
    ]
    assert resolver.get_app_models("sites") == ["sites.Site"]


@pytest.mark.skip("DEPRECATED")
def test_get_all_models():
    """
    Method should return a list of model labels for all enable applications.

    DEPRECATED: Ported to store tests
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
    # TODO: We probably should resolve FQL to determine implicit excludes.
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


class SmarterAppModelResolverAbstract(AppModelResolverAbstract):
    def smart_resolve_labels(self, labels, excludes=None):
        """
        DEPRECATED: The appstore should override this "smart" attempt

        TODO

        Full apps models list for reference: ::

            >>
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

            >> auth, djangoapp_sample.Article, djangoapp_sample.Category
            "auth.Permission",
            "auth.Group_permissions",
            "auth.Group",
            "auth.User_groups",
            "auth.User_user_permissions",
            "auth.User",
            "djangoapp_sample.Category",
            "djangoapp_sample.Article",

        Arguments:
            labels(string or list): Each label can be either model labels (as a string
                for a single one or a list for more) or application labels.

                Application label
                    This will be resolved to a list of names for all of its models, so
                    its useful to select all app models.

                Model label
                    Also known as a *fully qualified label*. We use it unchanged
                    without resolution. so its useful to explicitely define some
                    models, the ones that are not defined will be ignored.

                    A Model label must be in the form "APP.MODEL" because without the
                    second part after the dot is assumed as an Application label.

        Raises:
            AppModelResolverError: If a label contain an empty app label such
                ``.user``.
            LookupError: This is raised by Django application framework when an
                application label does not exist in application registry. We let it
                raises to keep a proper stacktrace on purpose.

        Returns:
            list: List of resolved model names from given labels.
        """
        model_names = []

        # Ensure we allways have a list
        labels = [labels] if isinstance(labels, str) else labels

        for label in labels:
            # Try to parse item as a fully qualified label
            try:
                app_label, model_label = label.split(".")
            # If not a fully qualified label assume it is an application label and add
            # all models
            except ValueError:
                model_names.extend(self.get_app_models(label))
            else:
                # Add the fully qualified label
                model_names.append(self.normalize_model_name(model_label, app=app_label))

        print()
        print("model_names:", model_names)
        print()

        included = list(filter(self.filter_out_excludes(excludes), model_names))

        return {
            # All involved app label, maybe useless or not realisable
            "apps": [],
            # Resolved labels from given label definitions for inclusion unused
            # directly in command
            "models": model_names,
            # Given label definitions for explicit exclusion unused directly in command
            "excludes": excludes,
            # Computed labels (from app all models - inclusion), Possibly useless
            "ignores": [],
            # Computed labels for inclusion definitions used in command
            "included": included,
            # Computed labels for merged exclusions (excludes + ignores) used in command
            "excluded": [],
        }

@pytest.mark.skip("DEPRECATED")
@pytest.mark.parametrize("labels, excludes, expected", [
    (
        "auth",
        [],
        {
            "apps": [],
            "models": [
                "auth.Permission",
                "auth.Group_permissions",
                "auth.Group",
                "auth.User_groups",
                "auth.User_user_permissions",
                "auth.User",
            ],
            "excludes": [],
            "ignores": [],
            "included": [
                "auth.Permission",
                "auth.Group_permissions",
                "auth.Group",
                "auth.User_groups",
                "auth.User_user_permissions",
                "auth.User",
            ],
            "excluded": [],
        }
    ),
    (
        "auth",
        ["auth.Group", "auth.Permission"],
        {
            "apps": [],
            "models": [
                "auth.Permission",
                "auth.Group_permissions",
                "auth.Group",
                "auth.User_groups",
                "auth.User_user_permissions",
                "auth.User",
            ],
            "excludes": ["auth.Group", "auth.Permission"],
            "ignores": [],
            "included": [
                "auth.Group_permissions",
                "auth.User_groups",
                "auth.User_user_permissions",
                "auth.User",
            ],
            "excluded": ["auth.Permission", "auth.Group"],
        }
    ),
    (
        ["auth.User", "auth.Permission"],
        [],
        {
            "apps": [],
            "models": ["auth.User", "auth.Permission"],
            "excludes": [],
            "ignores": [
                # "auth.Group_permissions",
                # "auth.Group",
                # "auth.User_groups",
                # "auth.User_user_permissions",
            ],
            "included": ["auth.User", "auth.Permission"],
            "excluded": [
                "auth.Group_permissions",
                "auth.Group",
                "auth.User_groups",
                "auth.User_user_permissions",
            ],
        }
    ),
    (
        ["auth.User", "auth.Permission"],
        ["auth.Group", "auth.Permission"],
        {
            "apps": [],
            "models": ["auth.User", "auth.Permission"],
            "excludes": ["auth.Group", "auth.Permission"],
            "ignores": [
                # "auth.Group_permissions",
                # "auth.User_groups",
                # "auth.User_user_permissions",
            ],
            "included": ["auth.User"],
            "excluded": [
                "auth.Permission",
                "auth.Group_permissions",
                "auth.Group",
                "auth.User_groups",
                "auth.User_user_permissions",
            ],
        }
    ),
    (
        ["auth", "djangoapp_sample.Article"],
        ["auth.Group", "auth.Permission"],
        {
            "apps": [],
            "models": [
                "auth.Permission",
                "auth.Group_permissions",
                "auth.Group",
                "auth.User_groups",
                "auth.User_user_permissions",
                "auth.User",
                "djangoapp_sample.Article",
            ],
            "excludes": ["auth.Group", "auth.Permission"],
            "ignores": [],
            "included": [
                "auth.Group_permissions",
                "auth.User_groups",
                "auth.User_user_permissions",
                "auth.User",
                "djangoapp_sample.Article",
            ],
            "excluded": ["auth.Permission", "auth.Group"],
        }
    ),
])
def test_resolve_names_todo(labels, excludes, expected):
    """
    DEPRECATED: Since appstore has implement implicit/explicit, however the parametrize
    data is interesting to use.

    TODO: A sample of what would be expected for a smart resolving

    Smart resolver would be able to discover implicit excludes from FQL, obviously
    taking in account of explicit excludes and possibly manage to perform this with a
    list of various involved apps.

    NOTE: Currently, order of FQM labels are not right, it keeps the definition order
    but we would prefer the original order from registered app models.
    """
    resolver = SmarterAppModelResolverAbstract()

    results = resolver.smart_resolve_labels(labels, excludes=excludes)
    #assert results == expected

    assert results["models"] == expected["models"]
    assert results["excludes"] == expected["excludes"]
    assert results["included"] == expected["included"]

    assert 1 == 42
