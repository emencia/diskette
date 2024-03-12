.. _natural keys: https://docs.djangoproject.com/en/5.0/topics/serialization/#topics-serialization-natural-keys

.. _appdef_intro:

======================
Application definition
======================

An application definition describes the models to dump and possible dump options. The
simpliest definition form is: ::

    ["django.contrib.sites", {"models": "sites"}]

Or a full example: ::

    [
        [
            "django.contrib.auth",
            {
                "comments": "Authentication and Authorization",
                "natural_foreign": true,
                "natural_primary": true,
                "allow_drain": true,
                "is_drain": false,
                "dump_command": "mydumper",
                "filename": "my_dump.json",
                "models": [
                    "auth.Group",
                    "auth.User"
                ],
                "excludes": [
                    "auth.Permission"
                ]
            }
        ],
    ]

Note than in this example, the ``excludes`` item is useless since models have been
explicitely defined for the right models to get.

Commonly you will dedicate an application definition to a single application but you
can also gather multiple applications models or split application models into multiple
applications.

Parameters
**********

As seen from previous example, an application definition is a list of two items:
firstly the application name then a dictionnary of parameters. The name is mostly used
to retrieve the application from registry and to build the default dump filename.

Parameters are:

comments
    *Optional*, *<string>*, *Default: empty*

    Free comment text, mostly used to give possible hints about the definition. It is
    not used to dump or load data.

natural_foreign
    *Optional*, *<boolean>*, *Default: false*

    Enable usage of `natural keys`_, not all model support natural keys but you should
    always try to enable it if possible since non natural foreign key may cause issue
    when loaded.

natural_primary
    *Optional*, *<boolean>*, *Default: false*

    Omits the primary key in the serialized data of objects since it can be calculated
    during deserialization.

allow_drain
    *Optional*, *<boolean>*, *Default: false*

    If enabled, this application allows its excluded models to be drained. Else the
    excluded models are always forbidden to be dumped by drainage.

is_drain
    *Optional*, *<boolean>*, *Default: false*

    If enabled, the application is defined as a special application dedicated to
    drainage.

dump_command
    *Optional*, *<string>*, *Default: empty*

    A Django command name to use instead of ``dumpdata``. Diskette include a special
    command named ``polymorphic_dumpdata`` that is dumpdata alike that is able to
    properly dump models made with ``django-polymorphic``.

filename
    *Optional*, *<string>*, *Default: empty*

    A custom filename for the application dump. If not given it will be automatically
    built from the slugified application name.

models
    *Optional*, *<list>*, *Default: empty*

    A list of labels to include in a dump. Labels can be either an application label
    (like ``sites``) or a fully qualified model label (like ``sites.Site``).

    If you only have one label to define, you can give it as a simple string instead
    of a list.

excludes
    *Optional*, *<list>*, *Default: empty*

    A list of labels to exclude from dump. Labels can be either an application label
    (like ``sites``) or a fully qualified model label (like ``sites.Site``).

    If you only have one label to define, you can give it as a simple string instead
    of a list.


Drain definition
****************

TODO
