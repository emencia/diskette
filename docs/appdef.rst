.. _natural keys: https://docs.djangoproject.com/en/5.0/topics/serialization/#topics-serialization-natural-keys

.. _appdef_intro:

======================
Application definition
======================

An application definition describes the models to dump and possible dump options.

Commonly you will dedicate an application definition to a single application but you
can also gather multiple applications models or split application models into multiple
definitions.

Simpliest sample
****************

The simpliest definition form is: ::

    ["django.contrib.sites", {"models": "sites"}]

It would generate a dump named ``django-contrib-sites.json`` that would contains the
entries from ``django_site`` table.


Full sample
***********

Or a full example: ::

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
    ]

.. Note::
    In this example the ``excludes`` item is useless since ``models`` explicitely
    defines the right models to get.

It would generate a dump named ``my_dump.json`` that would contains the
entries from ``auth_group``, ``auth_user`` and ``auth_user_groups`` tables.

.. _appdef_app_parameters:

Parameters
**********

An application definition is a list of two items:

#. The application name
#. Then a dictionnary of parameters.

The name is mostly used to retrieve the application from registry and to build the
default dump filename.

Available parameter items are:

comments
    *Optional*, *<string>*, *Default: empty*

    Free comment text, mostly used to give possible hints about the definition. It is
    not used to dump or load data.

natural_foreign
    *Optional*, *<boolean>*, *Default: false*

    Enable usage of `natural keys`_, not all model support natural keys but this is rare
    and you should always try to enable it if possible because non-natural foreign key
    may cause issues when loaded.

natural_primary
    *Optional*, *<boolean>*, *Default: false*

    Omits the primary key in the serialized data of objects since it can be calculated
    during deserialization.

use_base_manager
    *Optional*, *<boolean>*, *Default: false*

    Enable option to bypass a possible custom model manager to get model objects. This
    is helpful with some application that override the default manager method
    ``get_queryset`` to filter out some objects for some reasons.

allow_drain
    *Optional*, *<boolean>*, *Default: false*

    If enabled, this application allows its excluded models to be drained. Else the
    excluded models are always forbidden to be dumped by drainage.

is_drain
    *Optional*, *<boolean>*, *Default: false*

    If enabled, the application is assumed to be a :ref:`appdef_drain_definition`. A
    drain ignores usage of options ``models`` and ``allow_drain``.

dump_command
    *Optional*, *<string>*, *Default: empty*

    A Django command name to use instead of ``dumpdata``. Diskette include a special
    command :ref:`commands_polymorphic` that is like ``dumpdata`` but is able to
    properly dump models made with ``django-polymorphic``.

filename
    *Optional*, *<string>*, *Default: empty*

    A custom filename for the application dump.

    If not given it will be automatically built from the slugified application name. For
    example the filename for the application name ``Django Auth`` would be
    ``django-auth``.

models
    *Optional*, *<list>*, *Default: empty*

    A list of labels to include in a dump. Labels can be either an application label
    (like ``sites``) or a fully qualified model label (like ``sites.Site``).

    If you only have one label to define, you can give it as a simple string instead
    of a list.

    .. Hint::
        We recommend you to just define the application label and then excludes
        unwanted ones if there is any. This is because the explicit model definition can
        lead to missing new models or still defining some that have been removed from
        an application upgrade.

excludes
    *Optional*, *<list>*, *Default: empty*

    A list of labels to exclude from dump. Labels can be either an application label
    (like ``sites``) or a fully qualified model label (like ``sites.Site``).

    If you only have one label to define, you can give it as a simple string instead
    of a list.


.. _appdef_definition_order:

Definition order
****************

Diskette does not resolve definition order for you, it is your responsibility to ensure
they are defined in the right order.

Because Diskette stands on Django serializer through usage of ``dumpdata`` and
``loaddata``, models must be serialized in the right order. It means if a model B has
relation on model A, the model B must be defined after the model A definition.

Commonly dumping data won't fail with a wrong order but loadding data will always fail
because serializer will expect some related objects that don't exist yet.


.. _appdef_drain_definition:

Drain definition
****************

This is a special application definition which allows to drain excluded models from all
other apps.

It can be used in some situations where it will acts like a bucket to collect forbidden
models from definitions.

Diskette compute the implicit and explicit exclusions from all applications and drain
use them to know excluded application models that it can collect.

Because some application definition may be defined to exclude some models well known
to be avoided, a drain only collect exclusions from applications that allow it with
their option ``allow_drain``. Undefined application are fully collected.

.. Warning::
    Usage of drain is a risk of collecting many useless data or to break dump loading
    because of invalid data, so use it with caution.

    Commonly it is better to stand on application definitions.

