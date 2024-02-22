import pytest

from diskette.core.dumper import Dumper


@pytest.mark.parametrize("definitions, manager_opts, command_opts, expected", [
    # Most basic definition
    (
        [("Auth", {"models": "auth.User"})],
        {},
        {},
        [("Auth", "dumpdata auth.User")],
    ),
    # Specify an executable path
    (
        [("Auth", {"models": "auth.User"})],
        {"executable": "/bin/foo"},
        {},
        [("Auth", "/bin/foo dumpdata auth.User")],
    ),
    # With a destination where to write file
    (
        [("Auth", {"models": "auth.User"})],
        {},
        {"indent": 2, "destination": "/output"},
        [("Auth", "dumpdata --indent=2 auth.User --output=/output/auth.json")],
    ),
    # With a destination where to write file
    (
        [
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
                    "models": ["auth.Group","auth.User"]
                }
            ),
            (
                "sample blog", {
                    "comments": "internal blog sample app",
                    "models": "djangoapp_sample",
                    "excludes": ["djangoapp_sample.Category"],
                    "comments": "Lorem ipsum",
                    "natural_foreign": False,
                    "natural_primary": True,
                    "filename": "blog.json",
                    "allow_drain": False,
                }
            ),
        ],
        {},
        {"indent": 2, "destination": "/output"},
        [
            ("django.contrib.sites", (
                "dumpdata --indent=2 sites.Site --natural-foreign "
                "--output=/output/djangocontribsites.json"
            )),
            ("django.contrib.auth", (
                "dumpdata --indent=2 auth.Group auth.User --natural-foreign "
                "--output=/output/djangocontribauth.json"
            )),
            ("sample blog", (
                "dumpdata --indent=2 djangoapp_sample.Blog "
                "djangoapp_sample.Article_categories djangoapp_sample.Article "
                "--natural-primary --output=/output/blog.json"
            )),
        ],
    ),
])
def test_build_commands(definitions, manager_opts, command_opts, expected):
    """
    Manager should correctly build command line for each app.
    """
    manager = Dumper(definitions, **manager_opts)
    assert manager.build_commands(**command_opts) == expected


@pytest.mark.parametrize("definitions, expected", [
    # App does not allow to drain its exclusions and Drain itself dont want to
    (
        [
            ("Blog0", {
                "models": "djangoapp_sample",
                # DONT YOU TOUCH MY TRASHES, PEASANT
                "allow_drain": False,
            }),
            #                               > IT REJECT ANYTHING <
            ("Drainage", {"is_drain": True, "drain_excluded": False}),
        ],
        [
            ("Blog0", (
                "dumpdata djangoapp_sample.Blog "
                "djangoapp_sample.Category "
                "djangoapp_sample.Article_categories "
                "djangoapp_sample.Article"
            )),
            ("Drainage", (
                "dumpdata --exclude djangoapp_sample.Blog "
                "--exclude djangoapp_sample.Category "
                "--exclude djangoapp_sample.Article_categories "
                "--exclude djangoapp_sample.Article"
            )),
        ],
    ),
    # Accept to drain exclusions but app does not allow it
    (
        [
            ("Blog1", {
                "models": "djangoapp_sample",
                "excludes": ["djangoapp_sample.Category"],
                # DONT YOU TOUCH MY TRASHES, PEASANT
                "allow_drain": False,
            }),
            #                               > IM OPEN TO YOUR TRASHES <
            ("Drainage", {"is_drain": True, "drain_excluded": True}),
        ],
        [
            ("Blog1", (
                "dumpdata djangoapp_sample.Blog "
                "djangoapp_sample.Article_categories "
                "djangoapp_sample.Article"
            )),
            ("Drainage", (
                "dumpdata --exclude djangoapp_sample.Blog "
                "--exclude djangoapp_sample.Article_categories "
                "--exclude djangoapp_sample.Article "
                "--exclude djangoapp_sample.Category"
            )),
        ],
    ),
    # Refuse to drain exclusions from app even it allows for it
    (
        [
            ("Blog2", {
                "models": "djangoapp_sample",
                "excludes": ["djangoapp_sample.Category"],
                # GO AHEAD TAKE MY TRASHES
                "allow_drain": True,
            }),
            #                               > IT REJECT ANYTHING <
            ("Drainage", {"is_drain": True, "drain_excluded": False}),
        ],
        [
            ("Blog2", (
                "dumpdata djangoapp_sample.Blog "
                "djangoapp_sample.Article_categories "
                "djangoapp_sample.Article"
            )),
            ("Drainage", (
                "dumpdata --exclude djangoapp_sample.Blog "
                "--exclude djangoapp_sample.Article_categories "
                "--exclude djangoapp_sample.Article "
                "--exclude djangoapp_sample.Category"
            )),
        ],
    ),
    # Drain exclusion from app which allow it
    (
        [
            ("Blog3", {
                "models": "djangoapp_sample",
                "excludes": ["djangoapp_sample.Category"],
                # GO AHEAD TAKE MY TRASHES
                "allow_drain": True
            }),
            #                               > IM OPEN TO YOUR TRASHES <
            ("Drainage", {"is_drain": True, "drain_excluded": True}),
        ],
        [
            ("Blog3", (
                "dumpdata djangoapp_sample.Blog "
                "djangoapp_sample.Article_categories "
                "djangoapp_sample.Article"
            )),
            ("Drainage", (
                "dumpdata --exclude djangoapp_sample.Blog "
                "--exclude djangoapp_sample.Article_categories "
                "--exclude djangoapp_sample.Article"
            )),
        ],
    ),
    # Drain can specify its own additional excludes, they have the first priority
    # but don't duplicate with app retention
    (
        [
            ("Blog4", {
                "models": "djangoapp_sample",
                "excludes": ["djangoapp_sample.Category"],
                # GO AHEAD TAKE MY TRASHES
                "allow_drain": True
            }),
            ("Drainage", {
                "is_drain": True,
                "excludes": [
                    # It won't be duplicated
                    "djangoapp_sample.Article",
                    # Drain should have drained this one but it explicitely don't want
                    # this one
                    "djangoapp_sample.Category"
                ],
                # > IM OPEN TO YOUR TRASHES <
                "drain_excluded": True
            }),
        ],
        [
            ("Blog4", (
                "dumpdata djangoapp_sample.Blog "
                "djangoapp_sample.Article_categories "
                "djangoapp_sample.Article"
            )),
            ("Drainage", (
                "dumpdata --exclude djangoapp_sample.Blog "
                "--exclude djangoapp_sample.Article_categories "
                "--exclude djangoapp_sample.Article "
                "--exclude djangoapp_sample.Category"
            )),
        ],
    ),
])
def test_build_commands_with_drains(definitions, expected):
    """
    Manager should correctly build command line for each app including drain.
    """
    manager = Dumper(definitions)
    assert manager.build_commands() == expected
