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

Then load default Diskette :ref:`settings_intro` in your settings file: ::

    from diskette.settings import *

There is no migrations to apply.

At this point Diskette is correctly installed but won't archive anything, you will
need to define some applications and storages in settings, respectively
``DISKETTE_APPS`` and ``DISKETTE_STORAGES``.
