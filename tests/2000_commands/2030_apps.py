import ast
import json
from io import StringIO

from django.core import management


APP_DEFINITIONS = [
    [
        "django.contrib.admin",
        {
            "comments": "Administration",
            "natural_foreign": True,
            "models": [
                "admin.LogEntry"
            ]
        }
    ],
    [
        "django.contrib.auth",
        {
            "comments": "Authentication and Authorization",
            "natural_foreign": True,
            "models": [
                "auth.Permission",
                "auth.Group_permissions",
                "auth.Group",
                "auth.User_groups",
                "auth.User_user_permissions",
                "auth.User"
            ]
        }
    ],
    [
        "django.contrib.contenttypes",
        {
            "comments": "Content Types",
            "natural_foreign": True,
            "models": [
                "contenttypes.ContentType"
            ]
        }
    ],
    [
        "django.contrib.sessions",
        {
            "comments": "Sessions",
            "natural_foreign": True,
            "models": [
                "sessions.Session"
            ]
        }
    ],
    [
        "django.contrib.sites",
        {
            "comments": "Sites",
            "natural_foreign": True,
            "models": [
                "sites.Site"
            ]
        }
    ],
    [
        "sandbox.djangoapp_sample",
        {
            "comments": "Django app sample",
            "natural_foreign": True,
            "models": [
                "djangoapp_sample.Blog",
                "djangoapp_sample.Category",
                "djangoapp_sample.Article_categories",
                "djangoapp_sample.Article"
            ]
        }
    ]
]


def test_apps_cmd_json(caplog, db, settings, tests_settings, tmp_path):
    """
    Apps command should return a JSON of enabled application turned as Diskette
    data definitions.
    """
    output_path = tmp_path / "definitions.json"

    args = [
        "--destination={}".format(output_path),
        "--format=json",
    ]
    out = StringIO()
    management.call_command("diskette_apps", *args, stdout=out)
    # content = out.getvalue()
    out.close()

    # Check collected paths match the expected storage files from archive
    assert json.loads(output_path.read_text()) == APP_DEFINITIONS


def test_apps_cmd_python(caplog, db, settings, tests_settings, tmp_path):
    """
    Apps command should return Python list of enabled application turned as Diskette
    data definitions.
    """
    output_path = tmp_path / "definitions.json"

    args = [
        "--destination={}".format(output_path),
        "--format=python",
    ]
    out = StringIO()
    management.call_command("diskette_apps", *args, stdout=out)
    out.close()

    parsed = ast.literal_eval(output_path.read_text())

    assert parsed == APP_DEFINITIONS


def test_apps_cmd_inclusions(caplog, db, settings, tests_settings, tmp_path):
    """
    List is filtered to given inclusions only, other enable apps are ignored.
    """
    output_path = tmp_path / "definitions.json"

    args = [
        "--destination={}".format(output_path),
        "--format=json",
        "--app=auth",
        "--app=sites",
    ]
    out = StringIO()
    management.call_command("diskette_apps", *args, stdout=out)
    out.close()

    # Check collected paths match the expected storage files from archive
    assert json.loads(output_path.read_text()) == [
        [
            "django.contrib.auth",
            {
                "comments": "Authentication and Authorization",
                "natural_foreign": True,
                "models": [
                    "auth.Permission",
                    "auth.Group_permissions",
                    "auth.Group",
                    "auth.User_groups",
                    "auth.User_user_permissions",
                    "auth.User"
                ]
            }
        ],
        [
            "django.contrib.sites",
            {
                "comments": "Sites",
                "natural_foreign": True,
                "models": [
                    "sites.Site"
                ]
            }
        ],
    ]


def test_apps_cmd_exclusions(caplog, db, settings, tests_settings, tmp_path):
    """
    List is filtered out of given exclusions.
    """
    output_path = tmp_path / "definitions.json"

    args = [
        "--destination={}".format(output_path),
        "--format=json",
        "--exclude=admin",
        "--exclude=contenttypes",
        "--exclude=djangoapp_sample",
        "--exclude=sessions",
    ]
    out = StringIO()
    management.call_command("diskette_apps", *args, stdout=out)
    out.close()

    # Check collected paths match the expected storage files from archive
    assert json.loads(output_path.read_text()) == [
        [
            "django.contrib.auth",
            {
                "comments": "Authentication and Authorization",
                "natural_foreign": True,
                "models": [
                    "auth.Permission",
                    "auth.Group_permissions",
                    "auth.Group",
                    "auth.User_groups",
                    "auth.User_user_permissions",
                    "auth.User"
                ]
            }
        ],
        [
            "django.contrib.sites",
            {
                "comments": "Sites",
                "natural_foreign": True,
                "models": [
                    "sites.Site"
                ]
            }
        ],
    ]


def test_apps_cmd_mixed(caplog, db, settings, tests_settings, tmp_path):
    """
    List is properly filtered with given inclusions and exclusions. Names existing in
    both inclusions and exclusions are filtered out since exclusions has priority over
    inclusions.
    """
    output_path = tmp_path / "definitions.json"

    args = [
        "--destination={}".format(output_path),
        "--format=json",
        "--app=auth",
        "--app=djangoapp_sample",
        "--app=sites",
        "--app=sessions",
        "--exclude=contenttypes",
        "--exclude=djangoapp_sample",
        "--exclude=sessions",
    ]
    out = StringIO()
    management.call_command("diskette_apps", *args, stdout=out)
    out.close()

    # Check collected paths match the expected storage files from archive
    assert json.loads(output_path.read_text()) == [
        [
            "django.contrib.auth",
            {
                "comments": "Authentication and Authorization",
                "natural_foreign": True,
                "models": [
                    "auth.Permission",
                    "auth.Group_permissions",
                    "auth.Group",
                    "auth.User_groups",
                    "auth.User_user_permissions",
                    "auth.User"
                ]
            }
        ],
        [
            "django.contrib.sites",
            {
                "comments": "Sites",
                "natural_foreign": True,
                "models": [
                    "sites.Site"
                ]
            }
        ],
    ]
