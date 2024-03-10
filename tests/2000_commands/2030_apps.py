import json
from io import StringIO

from django.core import management


def test_apps_cmd(caplog, db, settings, tests_settings, tmp_path):
    """
    Apps command should return a JSON of enabled application turned as Diskette
    data definitions.
    """
    # Copy sample archive to temp dir
    output_path = tmp_path / "definitions.json"

    # Execute load command
    args = [
        "--destination={}".format(output_path),
    ]
    out = StringIO()
    management.call_command("diskette_apps", *args, stdout=out)
    # content = out.getvalue()
    out.close()

    # Check collected paths match the expected storage files from archive
    assert json.loads(output_path.read_text()) == [
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