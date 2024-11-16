.. _install_intro:

=======
Install
=======

Install package in your environment : ::

    pip install diskette

For development usage see :ref:`development_install`.


Configuration
*************

Add it to your installed Django apps in settings : ::

    INSTALLED_APPS = (
        ...
        "diskette",
    )

Diskette app does not require any specific order position, commonly you would want to
put it after the Django builtin apps at least.

Then load default Diskette :ref:`settings_intro` in your settings file: ::

    from diskette.settings import *

.. Note::

    Instead if your project use
    `django-configuration <https://django-configurations.readthedocs.io/en/stable/>`_,
    your settings class can inherits from
    :ref:`references_contrib_django_configuration`).

There is no migrations to apply.

At this point Diskette is correctly installed but won't archive anything, you will
need to define some applications and storages in settings, respectively
``DISKETTE_APPS`` and ``DISKETTE_STORAGES``.
