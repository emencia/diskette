.. _install_intro:

=======
Install
=======

Install package in your environment : ::

    pip install diskette

For development usage see :ref:`development_install`.


Enable application
******************

Add it to your installed Django apps in settings : ::

    INSTALLED_APPS = (
        ...
        "django_sendfile",
        "diskette",
    )

Diskette app does not require any specific order position, commonly you would want to
put it after the Django builtin apps at least.

As you can see Diskette is using Django Sendfile application to serve protected dump
files, there is no specific order position also, commonly you will put it before
Diskette application.


Configuration
*************

Now your project must load default Diskette :ref:`settings_intro` in your settings
file: ::

    from diskette.settings import *

.. Note::

    Instead if your project use
    `django-configuration <https://django-configurations.readthedocs.io/en/stable/>`_,
    your settings class can inherits from
    :ref:`references_contrib_django_configuration`).

Then you need to define the
`Django Sendfile settings <https://django-sendfile2.readthedocs.io/en/latest/getting-started.html#installation>`_.

.. Hint::
    In our local sandbox we are using these settings for the simple sendfile backend: ::

        SENDFILE_BACKEND = "django_sendfile.backends.simple"
        SENDFILE_ROOT = VAR_PATH / "protected-media"
        SENDFILE_URL = "/protected"

    Where ``VAR_PATH`` is a ``pathlib.Path`` object to a ``var/`` directory in project
    directory. It is important that Diskette is configured to dump archive files in the
    sendfile directory like ::

        DISKETTE_DUMP_PATH = SENDFILE_ROOT / "dumps"

    The simple sendfile backend is not the best one for production usage, see the
    `Django Sendfile backend <https://django-sendfile2.readthedocs.io/en/latest/backends.html>`_
    documentation for details.

And finally you can run the Django command to apply the Diskette migrations.

At this point Diskette is correctly installed but won't archive anything, you will
need to define some applications and storages in :ref:`settings_intro`, respectively
``DISKETTE_APPS`` and ``DISKETTE_STORAGES``. You may also define ``DISKETTE_DUMP_PATH``
because with its default value it stores dump files in the current working directory
of your Python process.
