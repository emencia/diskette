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

Then load default application settings in your settings file: ::

    from diskette.settings import *

And finally apply database migrations.


Settings
********

.. automodule:: diskette.settings
   :members:
