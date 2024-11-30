.. _basic_sample_intro:

============
Basic sample
============

Here we will demonstrate a basic usage sample with a dummy Django project.


Project structure
*****************

For this demonstration we will have some structure requirements: ::

    .
    ├── manage.py
    ├── project
    │   └── settings.py
    └── var
        └── media

A project Django include more components but in this document we will just focus on
these ones.

We assume the project is located at ``/home/foo/myproject/``.


Configuration
*************

Firstly, we will enable related apps and Diskette itself then define some applications
and storages in settings: ::

    from pathlib import Path

    BASE_DIR = Path(__file__).parents[1]
    VAR_PATH = BASE_DIR / "var"
    MEDIA_ROOT = VAR_PATH / "media"
    INSTALLED_APPS = [
        "django.contrib.admin",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.sites",
        "diskette",
    ]
    DISKETTE_APPS = [
        [
            "django.contrib.auth", {
                "comments": "django.contrib.auth: user and groups, no perms",
                "natural_foreign": True,
                "models": ["auth.Group","auth.User"]
            }
        ],
        [
            "django.contrib.sites", {
                "comments": "django.contrib.sites",
                "natural_foreign": True,
                "models": "sites"
            }
        ]
    ]

    DISKETTE_STORAGES = [MEDIA_ROOT]
    DISKETTE_STORAGES_EXCLUDES = [
        "cache/*",
        "pil/*",
        "public/thumbnails/*",
    ]

* ``BASE_DIR`` and ``VAR_PATH`` are only there as good practice to build the path of
  ``MEDIA_ROOT``;
* ``DISKETTE_APPS`` defines data to dump for sites applications and some Django auth
  models;
* ``DISKETTE_STORAGES`` defines a single storage for the whole media directory using
  related setting;
* ``DISKETTE_STORAGES_EXCLUDES`` defines some exclusion patterns for storage;

Now Diskette is correctly configured, you will need some data, creating some users
should be enough for this demonstration.


Dump
****

The command is simple enough as: ::

    python manage.py diskette_dump

And it should output something like this: ::

    === Starting dump ===
    Dumping data for application 'django.contrib.auth'
    Dumping data for application 'django.contrib.sites'
    Appending data to the archive
    Appending storages to the archive
    Dump archive was created at: /home/foo/myproject/var/diskette_data_storages.tar.gz (8,1 Mio)

The archive size is a sample, it will depends from your data and media files.

We could have used an option to just output command lines to use for manually dump: ::

    python manage.py diskette_dump --no-archive

That would output: ::

    # django.contrib.auth
    dumpdata auth.Group auth.User --natural-foreign --output=/home/foo/myproject/var/data/djangocontribauth.json
    # django.contrib.sites
    dumpdata sites.Site --natural-foreign --output=/home/foo/myproject/var/data/djangocontribsites.json

You will still have to prefix these command with the Django script ``django-admin.py``
or ``manage.py``.

Load
****

So from the first step before, we got an archive file at
``/home/foo/myproject/var/diskette_data_storages.tar.gz`` that we can load.

First we need to empty the database because loading can not work with existing objects,
it would conflict on primary keys or relations. So initialize again an empty database
and run the migrations.

When it is done you can load the content from archive: ::

    python manage.py diskette_load diskette_data_storages.tar.gz

And then it should succeed to load data and storages from archive. The archive is
automatically removed once finished.


Create data definitions
***********************

With default Diskette settings on a fresh new project the definition list from
``DISKETTE_APPS`` is empty and you need to fill it yourself.

To help you start on this, there is a command that will search for all enabled
application in your project and output you a definition list: ::

    python manage.py diskette_apps

That should output some JSON like this: ::

    [
        [
            "django.contrib.admin",
            {
                "comments": "Administration",
                "natural_foreign": true,
                "models": [
                    "admin.LogEntry"
                ]
            }
        ],
        [
            "django.contrib.auth",
            {
                "comments": "Authentication and Authorization",
                "natural_foreign": true,
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
                "comments": "Types de contenus",
                "natural_foreign": true,
                "models": [
                    "contenttypes.ContentType"
                ]
            }
        ],
        [
            "django.contrib.sessions",
            {
                "comments": "Sessions",
                "natural_foreign": true,
                "models": [
                    "sessions.Session"
                ]
            }
        ],
        [
            "django.contrib.sites",
            {
                "comments": "Sites",
                "natural_foreign": true,
                "models": [
                    "sites.Site"
                ]
            }
        ]
    ]

.. Hint::
    This is in JSON format, you would need to turn them in Python to include it in
    setting ``DISKETTE_APPS``, here this is simple enough as replacing all ``true``
    occurences with ``True``.

As you can see the built definition list is opinionated:

* It list all enabled applications from setting ``INSTALLED_APPS`` but not all should
  be dumped. Commonly you should not dump ``contenttypes``, ``sessions`` or
  ``permissions``;
* It explicitely list all application models for inclusion instead of using the simple
  application name as it could be. This is to help you to see all available models and
  find the ones to excludes, you should instead prefer to just define the application
  label;
* It always enable the ``natural_foreign`` option because you should always use it
  except with very special models that really don't support them;
* It include the ``comments`` option filled with the application verbose name. It does
  not have any other goal that describe definition for human user;

See :ref:`appdef_app_parameters` for a complete detail of definition options.