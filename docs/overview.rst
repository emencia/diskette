.. _overview_intro:

========
Overview
========

Diskette archive
****************

Diskette use a tarball archive (``*.tar.gz``) to gather application model data dumps
and media storage directories to archive and to restore.

A diskette archive contains a manifest file that is used to know what is to restore and
how but you will not need to manipulate it.

Depending options, the archive can contains data dumps, storage directories or both.
An archive can not be created without anything.

When creating an archive, remember you will need twice size of storages size then also
the size of data dumps.

.. Note::
    Diskette data dump are done to work on the same project. It could work with another
    project but it will need to be compatible, it means migration states should be
    identical, project must enable the same applications and have compatible settings.


Application model datas
***********************

They are managed through
`Django fixtures <https://docs.djangoproject.com/en/stable/topics/db/fixtures/>`_ in
JSON format.

Fixtures have benefit to be naturally managed from Django and are not tied to any SGBD
dump format, so you can import them with any supported database driver from Django.

.. Note::
    Fixture format is not as efficient as SGBD dump formats, especially on very large
    datasets. It may not be the best choices to backup very big databases.

Diskette dumps data with Django command ``dumpdata`` and load them with ``loaddata``.
However application definition can define another dump command to use but it must be
a Django command.

Diskette knows model datas to dump from :ref:`appdef_intro` list defined in
``settings.DISKETTE_APPS``.


Media storages
**************

Despite their name, this is not related to
`Django storages <https://docs.djangoproject.com/en/stable/ref/files/storage/>`_. A
storage is just a directory to archive. Commonly the simpliest configuration will just
define a storage for the media directory and possibly another one for the protected
medias (when you have some protections with *sendfile*).

To avoid invalid storage configuration that would lead to write anywhere on the user
system, all storage directories must be a children of a *storage basepath* which is
commonly the current working directory. You can tweak the configuration to bypass this
protection but it is rarely a good idea.

Diskette knows storages to archive from list defined in ``settings.DISKETTE_STORAGES``.
