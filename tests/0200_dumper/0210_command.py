import pytest

from diskette.core.dumper import Dumper


# TODO: Assertions with excludes are not really correct even test pass, because the
# resolver will change the way we exclude labels (explicit label definition from
# resolver instead of --excludes usages)
@pytest.mark.skip("Refactoring drainage, resolver and excludes, Part 2")
@pytest.mark.parametrize("apps, manager_options, command_options, expected", [
    # Most basic definition
    (
        [("Auth", {"models": "auth.user"})],
        {},
        {},
        [("Auth", "dumpdata auth.user")],
    ),
    # Specify an executable path
    (
        [("Auth", {"models": "auth.user"})],
        {"executable": "/bin/foo"},
        {},
        [("Auth", "/bin/foo dumpdata auth.user")],
    ),
    # With a destination where to write file
    (
        [("Auth", {"models": "auth.user"})],
        {},
        {"indent": 2, "destination": "/output"},
        [("Auth", "dumpdata --indent=2 auth.user --output=/output/auth.json")],
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
                    "models": ["auth.group","auth.user"]
                }
            ),
            (
                "sample blog", {
                    "comments": "internal blog sample app",
                    "models": "djangoapp_sample",
                    "excludes": ["blog.category"],
                    "comments": "Lorem ipsum",
                    "natural_foreign": False,
                    "natural_primary": True,
                    "filename": "blog.json",
                    "allow_drain": True,
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
                "dumpdata --indent=2 auth.group auth.user --natural-foreign "
                "--output=/output/djangocontribauth.json"
            )),
            ("sample blog", (
                "dumpdata --indent=2 djangoapp_sample.Blog djangoapp_sample.Category "
                "djangoapp_sample.Article_categories djangoapp_sample.Article "
                "--natural-primary --exclude blog.category --output=/output/blog.json"
            )),
        ],
    ),
    # Basic drain
    (
        [
            ("Auth", {"models": "auth"}),
            ("Drainage", {"is_drain": True}),
        ],
        {},
        {},
        [
            ("Auth", (
                "dumpdata auth.Permission auth.Group_permissions auth.Group "
                "auth.User_groups auth.User_user_permissions auth.User"
            )),
            ("Drainage", (
                "dumpdata --all --exclude auth.Permission "
                "--exclude auth.Group_permissions --exclude auth.Group "
                "--exclude auth.User_groups --exclude auth.User_user_permissions "
                "--exclude auth.User"
            )),
        ],
    ),
    # Drain don't automatically include application excluded models
    (
        [
            ("Blog", {"models": "blog", "excludes": ["blog.article_tags"]}),
            ("Drainage", {"is_drain": True}),
        ],
        {},
        {},
        [
            ("Blog", "dumpdata blog --exclude blog.article_tags"),
            ("Drainage", "dumpdata --all --exclude blog"),
        ],
    ),
    # Drain can specify some excludes on its own
    (
        [
            ("Blog", {"models": "blog"}),
            ("Drainage", {"is_drain": True, "excludes": ["blog", "site"]}),
        ],
        {},
        {},
        [
            ("Blog", "dumpdata blog"),
            ("Drainage", "dumpdata --all --exclude blog --exclude site"),
        ],
    ),
    # Drain does not include application excluded models if the app don't allow it
    # TODO: drain_excluded is enabled but results is exactly the same than disabled,
    # this is not working.
    (
        [
            ("Blog", {"models": "blog", "excludes": ["blog.article_tags"]}),
            ("Drainage", {"is_drain": True, "drain_excluded": True}),
        ],
        {},
        {},
        [
            ("Blog", "dumpdata blog --exclude blog.article_tags"),
            ("Drainage", "dumpdata --all --exclude blog"),
        ],
    ),
    # If application allow it and drain is required to, it will include application
    # excluded models
    (
        [
            ("Blog", {
                "models": "blog",
                "excludes": ["blog.article_tags"],
                "allow_drain": True
            }),
            ("Drainage", {"is_drain": True, "drain_excluded": True}),
        ],
        {},
        {},
        [
            ("Blog", "dumpdata blog --exclude blog.article_tags"),
            ("Drainage", "dumpdata --all --exclude blog --exclude blog.article_tags"),
        ],
    ),
])
def test_build_commands(apps, manager_options, command_options, expected):
    """
    Manager should correctly build command line for each app including drain.
    """
    manager = Dumper(apps, **manager_options)
    # print(json.dumps(manager.build_commands(**command_options), indent=4))
    assert manager.build_commands(**command_options) == expected
