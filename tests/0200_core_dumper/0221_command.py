import pytest

from diskette.core.dumper import Dumper

from tests.samples import SAMPLE_APPS


@pytest.mark.parametrize("apps, manager_options, command_options, expected", [
    # Most basic definition
    (
        [("foo.bar", {"models": "bar"})],
        {},
        {},
        [("foo.bar", "dumpdata bar")],
    ),
    # Specify an executable path
    (
        [("foo.bar", {"models": "bar"})],
        {"executable": "/bin/foo"},
        {},
        [("foo.bar", "/bin/foo dumpdata bar")],
    ),
    # With a destination where to write file
    (
        [("foo.bar", {"models": "bar"})],
        {},
        {"indent": 2, "destination": "/output"},
        [("foo.bar", "dumpdata --indent=2 bar --output=/output/foobar.json")],
    ),
    # More complete application set with all options
    (
        SAMPLE_APPS,
        {},
        {},
        [
            ("Blog", "dumpdata blog"),
            ("Tags", "dumpdata tags --natural-foreign --natural-primary"),
            ("Authors", "dumpdata authors.user authors.pin --exclude authors.pin"),
            ("Contacts", "dumpdata contacts --exclude contacts.token"),
            ("Cart", "dumpdata cart.item cart.payment --exclude cart.payment"),
            (
                "Pages",
                (
                    "dumpdata pages --natural-foreign --natural-primary "
                    "--exclude pages.revision"
                )
            ),
        ],
    ),
    # Basic drain
    (
        [
            ("Blog", {"models": "blog"}),
            ("Drainage", {"is_drain": True}),
        ],
        {},
        {},
        [
            ("Blog", "dumpdata blog"),
            ("Drainage", "dumpdata --all --exclude blog"),
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
    #
    (
        SAMPLE_APPS + [
            ("Drainage", {
                "is_drain": True,
                "excludes": ["site"],
                "drain_excluded": True,
            }),
        ],
        {},
        {},
        [
            ("Blog", "dumpdata blog"),
            ("Tags", "dumpdata tags --natural-foreign --natural-primary"),
            ("Authors", "dumpdata authors.user authors.pin --exclude authors.pin"),
            ("Contacts", "dumpdata contacts --exclude contacts.token"),
            ("Cart", "dumpdata cart.item cart.payment --exclude cart.payment"),
            (
                "Pages",
                (
                    "dumpdata pages --natural-foreign --natural-primary "
                    "--exclude pages.revision"
                )
            ),
            (
                "Drainage",
                (
                    "dumpdata --all --exclude site --exclude blog --exclude tags "
                    "--exclude authors.user --exclude authors.pin --exclude contacts "
                    "--exclude cart.item --exclude cart.payment --exclude pages "
                    "--exclude pages.revision"
                )
            ),
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
