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


Dump management from Django admin
*********************************

Dumps can be created from the Django admin interface by staff users.

Preservation
------------

The Diskette admin registers all created dump and manage to only keep the latest ones
for an identical option set which is either:

* Dump with data only;
* Dump with storages only;
* Dump with data and storages;

The latest dump of an option set is available to download and the other ones are
automatically marked as deprecated.

Deprecation
-----------

A deprecated dump can not be downloaded anymore and if the related setting is enabled
its file is automatically purged from filesystem.

Automatic purge and deprecation jobs are done during dump creation.

Once created a dump can not be changed except for its ``deprecated`` field that can be
checked to deprecate dump but this is not reversible, a deprecated dump can not be made
available again.

Integrity
---------

You may need to check if download dump archive has been correctly downloaded and to do
so the dump stores a *BLAKE2* checksum that you can compare to your downloaded file.

The `GNU Core Utilities <https://www.gnu.org/software/coreutils/>`_ (that is
installed on almost all non Windows systems) provides a command ``b2sum`` to compute
a *BLAKE2* checksum for a file: ::

    b2sum yourdownloadedfile.tar.gz

Download
--------

Currently the only way to get a dump archive file is to download it from the Django
admin, you will retrieve its download link from the dump detail view.

The download is only available for a non deprecated dump with a non empty or purged
file path.

Dump download view is protected with Django Sendfile and can only be reached from the
admin for an authenticated staff user.

.. Note::
    With :ref:`commands_load` you won't be able to directly download and load a dump
    using its download URL since it needs an authentication.

    You will have to download file on your filesystem then give its local path to the
    command.