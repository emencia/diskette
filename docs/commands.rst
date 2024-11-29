.. _commands_intro:

========
Commands
========

.. Included rst tables are automatically built from command_parser.py in project task
   'make doc', don't edit them since they will be overwritten on updates.

Here is a detail of all available Django commands supplied by Diskette. Although their
detail does not include it, they all inherit from
`Django command default options <https://docs.djangoproject.com/en/5.0/ref/django-admin/#default-options>`_.


.. _commands_dump:

diskette_dump
*************

Dump configured application data and media files into an archive.

Initially the command should get its configuration from :ref:`settings_intro` but you
are able to override them with available command options.

Usage
    ::

        python manage.py diskette_dump [options]

Options
    .. include:: ./_static/commands/dump.rst


.. _commands_load:

diskette_load
*************

Restore application datas and storage files from an archive file previously created
with ``diskette_dump``.

Usage
    ::

        python manage.py diskette_load <archive> [options]

Options
    .. include:: ./_static/commands/load.rst


.. _commands_apps:

diskette_apps
*************

This command helps to see all possible application definitions from currently
installed applications in your project.

This is especially useful when you start to create application definitions to quickly
get a base to start from or to update definitions after enabling new applications.

Usage: ::

    python manage.py diskette_apps [options]

Options
    .. include:: ./_static/commands/apps.rst


.. _commands_polymorphic:

polymorphic_dumpdata
********************

A command alike Django's dumpdata but it enforces usage of
legacy ``django.db.models.query.QuerySet`` over custom model queryset.

This is needed to dump data for polymorphic models that won't work properly,
especially when used from ``django.core.management.call_command``.

Original code comes from a
`czpython Gist <https://gist.github.com/czpython/b94c346e4b6cac473bff>`_
found from
`django-filer issue 887 <https://github.com/django-cms/django-filer/issues/887#issuecomment-231911757>`_.
This should resolves problem demonstrated in
`django-polymorphic issue 175 <https://github.com/jazzband/django-polymorphic/issues/175#issuecomment-1607260352>`_.

However this only supports a few set of legacy dumpdata options. Unavailable options
are still present but will raise a NotImplementedError when used, in the following
table they are marked as *NOT IMPLEMENTED*.


Usage: ::

    python manage.py polymorphic_dumpdata <args> [options]

Options
    .. include:: ./_static/commands/polymorphic_dumpdata.rst
