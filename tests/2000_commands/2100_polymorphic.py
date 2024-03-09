import json
from io import StringIO

import pytest

from django.core import management

from freezegun import freeze_time

from sandbox.djangoapp_sample.factories import (
    ArticleFactory, BlogFactory, CategoryFactory
)


def test_polymorphic_cmd_basic(caplog, db, tmp_path):
    """
    Polymorphic dumpdata should dump data without any errors just like legacy dumpdata
    command.

    This does not test dump for Polymorphic models, only that the command basically
    works.
    """
    # Copy sample archive to temp dir
    output_path = tmp_path / "definitions.json"

    # Execute command to output dump to a file
    with StringIO() as out:
        management.call_command(
            "polymorphic_dumpdata",
            *[
                "--output={}".format(output_path),
                "sites",
            ],
            stdout=out
        )

    dump = json.loads(output_path.read_text())
    assert dump == [
        {
            "model": "sites.site",
            "pk": 1,
            "fields": {
                "domain": "example.com",
                "name": "example.com"
            }
        }
    ]

    # Execute command to output dump to standard output
    with StringIO() as out:
        management.call_command(
            "polymorphic_dumpdata",
            *["sites"],
            stdout=out
        )
        content = out.getvalue()

    dump = json.loads(content)
    assert dump == [
        {
            "model": "sites.site",
            "pk": 1,
            "fields": {
                "domain": "example.com",
                "name": "example.com"
            }
        }
    ]


@pytest.mark.parametrize("arguments", [
    ["--all"],
    ["--format=xml"],
    ["--pks=42"],
    ["--database=foo"],
])
def test_polymorphic_cmd_unsupported_args(caplog, db, arguments):
    """
    Command should raise exception for all unimplemented arguments when given.
    """
    with StringIO() as out:
        with pytest.raises(NotImplementedError):
            management.call_command(
                "polymorphic_dumpdata",
                *["sites"] + arguments,
                stdout=out
            )


@freeze_time("2012-10-15 10:00:00")
def test_polymorphic_cmd_labels(caplog, db, tmp_path):
    """
    Polymorphic dumpdata should correctly support label inclusion and exclusion
    arguments.
    """
    blog = BlogFactory()
    category = CategoryFactory()
    article = ArticleFactory(blog=blog, fill_categories=[category])

    # Execute command to output dump to standard output
    with StringIO() as out:
        management.call_command(
            "polymorphic_dumpdata",
            *[
                "sites",
                "djangoapp_sample",
                "--exclude=djangoapp_sample.Category",
                "--exclude=djangoapp_sample.Blog",
                "--exclude=djangoapp_sample.Article_categories",
            ],
            stdout=out
        )
        content = out.getvalue()

    dump = json.loads(content)
    assert dump == [
        {
            "model": "sites.site",
            "pk": 1,
            "fields": {
                "domain": "example.com",
                "name": "example.com"
            }
        },
        {
            "model": "djangoapp_sample.article",
            "pk": article.id,
            "fields": {
                "blog": blog.id,
                "author": None,
                "title": article.title,
                "content": article.content,
                "publish_start": "2012-10-15T10:00:00Z",
                "categories": [category.id]
            }
        }
    ]
