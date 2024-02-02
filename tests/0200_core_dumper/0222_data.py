import json

from freezegun import freeze_time

from lotus.factories import ArticleFactory, CategoryFactory

from diskette.core.dumper import Dumper
from diskette.factories import UserFactory


@freeze_time("2012-10-15 10:00:00")
def test_dump_data(db, tmp_path):
    """
    Manager should calls dumpdata command and return their correct outputs.
    """
    picsou = UserFactory()
    donald = UserFactory()
    # Force a dummy string password easier to assert
    picsou.password = "dummy"
    picsou.save()
    donald.password = "dummy"
    donald.save()

    manager = Dumper([
        ("Django auth", {"models": ["auth.group", "auth.user"]}),
        ("Django site", {"models": ["sites"]}),
    ])
    results = manager.dump_data()
    # Parse command string outputs and turn them to JSON
    deserialized = [
        (k, json.loads(v))
        for k, v in results
    ]
    # print(json.dumps(deserialized, indent=4))
    assert deserialized == [
        (
            "Django auth",
            [
                {
                    "model": "auth.user",
                    "pk": picsou.id,
                    "fields": {
                        "password": "dummy",
                        "last_login": None,
                        "is_superuser": False,
                        "username": picsou.username,
                        "first_name": picsou.first_name,
                        "last_name": picsou.last_name,
                        "email": picsou.email,
                        "is_staff": False,
                        "is_active": True,
                        "date_joined": "2012-10-15T10:00:00Z",
                        "groups": [],
                        "user_permissions": []
                    }
                },
                {
                    "model": "auth.user",
                    "pk": donald.id,
                    "fields": {
                        "password": "dummy",
                        "last_login": None,
                        "is_superuser": False,
                        "username": donald.username,
                        "first_name": donald.first_name,
                        "last_name": donald.last_name,
                        "email": donald.email,
                        "is_staff": False,
                        "is_active": True,
                        "date_joined": "2012-10-15T10:00:00Z",
                        "groups": [],
                        "user_permissions": []
                    }
                },
            ]
        ),
        (
            "Django site",
            [
                {
                    "model": "sites.site",
                    "pk": 1,
                    "fields": {
                        "domain": "example.com",
                        "name": "example.com"
                    }
                }
            ]
        ),
    ]


@freeze_time("2012-10-15 10:00:00")
def test_dump_data_destination(db, tmp_path):
    """
    With a given destination the manager should calls dumpdata command and return
    dump filepaths.
    """
    picsou = UserFactory()
    donald = UserFactory()
    # Force a dummy string password easier to assert
    picsou.password = "dummy"
    picsou.save()
    donald.password = "dummy"
    donald.save()

    manager = Dumper([
        ("Django auth", {"models": ["auth.group", "auth.user"]}),
        ("Django site", {"models": ["sites"]}),
    ])
    results = manager.dump_data(destination=tmp_path)

    expected_auth_dump_path = tmp_path / "django-auth.json"
    expected_site_dump_path = tmp_path / "django-site.json"
    deserialized = [
        (k, json.loads(v))
        for k, v in results
    ]
    assert deserialized == [
        ("Django auth", {"destination": str(expected_auth_dump_path)}),
        ("Django site", {"destination": str(expected_site_dump_path)}),
    ]

    assert expected_auth_dump_path.exists() is True
    assert expected_site_dump_path.exists() is True

    # Check written dumps contents
    assert json.loads(expected_auth_dump_path.read_text()) == [
        {
            "model": "auth.user",
            "pk": picsou.id,
            "fields": {
                "password": "dummy",
                "last_login": None,
                "is_superuser": False,
                "username": picsou.username,
                "first_name": picsou.first_name,
                "last_name": picsou.last_name,
                "email": picsou.email,
                "is_staff": False,
                "is_active": True,
                "date_joined": "2012-10-15T10:00:00Z",
                "groups": [],
                "user_permissions": []
            }
        },
        {
            "model": "auth.user",
            "pk": donald.id,
            "fields": {
                "password": "dummy",
                "last_login": None,
                "is_superuser": False,
                "username": donald.username,
                "first_name": donald.first_name,
                "last_name": donald.last_name,
                "email": donald.email,
                "is_staff": False,
                "is_active": True,
                "date_joined": "2012-10-15T10:00:00Z",
                "groups": [],
                "user_permissions": []
            }
        },
    ]

    assert json.loads(expected_site_dump_path.read_text()) == [
        {
            "model": "sites.site",
            "pk": 1,
            "fields": {
                "domain": "example.com",
                "name": "example.com"
            }
        }
    ]


@freeze_time("2012-10-15 10:00:00")
def test_dump_data_drained(db, tmp_path):
    """
    With a drain application, every remaining models that have not been excluded should
    be dumped to the drain entry.
    """
    picsou = UserFactory()
    # Force a dummy string password easier to assert
    picsou.password = "dummy"
    picsou.save()

    category = CategoryFactory()
    article = ArticleFactory(fill_categories=[category])

    manager = Dumper([
        ("Django auth", {"models": ["auth.group", "auth.user"]}),
        ("Lotus articles", {"models": ["lotus.article"]}),
        ("Drainage", {
            "is_drain": True,
            "excludes": ["contenttypes", "auth.permission"],
            "drain_excluded": True,
        }),
    ])
    results = manager.dump_data()
    # Parse command string outputs and turn them to JSON
    deserialized = [
        (k, json.loads(v))
        for k, v in results
    ]
    # print(json.dumps(deserialized, indent=4))
    assert deserialized == [
        (
            "Django auth",
            [
                {
                    "model": "auth.user",
                    "pk": picsou.id,
                    "fields": {
                        "password": "dummy",
                        "last_login": None,
                        "is_superuser": False,
                        "username": picsou.username,
                        "first_name": picsou.first_name,
                        "last_name": picsou.last_name,
                        "email": picsou.email,
                        "is_staff": False,
                        "is_active": True,
                        "date_joined": "2012-10-15T10:00:00Z",
                        "groups": [],
                        "user_permissions": []
                    }
                },
            ]
        ),
        (
            "Lotus articles",
            [
                {
                    "model": "lotus.article",
                    "pk": article.id,
                    "fields": {
                        "language": article.language,
                        "original": None,
                        "status": article.status,
                        "featured": False,
                        "pinned": False,
                        "private": False,
                        "publish_date": "2012-10-15",
                        "publish_time": "10:00:00",
                        "publish_end": None,
                        "last_update": "2012-10-15T10:00:00Z",
                        "title": article.title,
                        "slug": article.slug,
                        "seo_title": article.seo_title,
                        "lead": article.lead,
                        "introduction": article.introduction,
                        "content": article.content,
                        "cover": article.cover.name,
                        "image": article.image.name,
                        "album": None,
                        "categories": [category.id],
                        "authors": [],
                        "related": []
                    }
                }
            ]
        ),
        (
            "Drainage",
            [
                {
                    "model": "sites.site",
                    "pk": 1,
                    "fields": {
                        "domain": "example.com",
                        "name": "example.com"
                    }
                },
                {
                    "model": "lotus.category",
                    "pk": category.id,
                    "fields": {
                        "language": category.language,
                        "original": None,
                        "modified": "2012-10-15T10:00:00Z",
                        "title": category.title,
                        "slug": category.slug,
                        "lead": category.lead,
                        "description": category.description,
                        "cover": category.cover.name
                    }
                }
            ]
        ),
    ]
