.. _admin_intro:

=====
Admin
=====

Diskette provide some views for the Django admin. The Diskette admin is enabled on
default but it can be disabled from setting ``DISKETTE_ADMIN_ENABLED``.


Managing dumps
**************

This allows administrators to create dumps, keep an history of their creations and
see their log messages for the creation process.


Preservation
------------

The Diskette admin registers all created dump but only keep the latest ones for an
identical option set which is either:

* Dump with data only;
* Dump with storages only;
* Dump with data and storages;

The latest dump of an option set is available to download and the other ones are
automatically marked as deprecated.


Deprecation
-----------

A deprecated dump can not be downloaded anymore and if the related setting
``DISKETTE_DUMP_AUTO_PURGE`` is enabled its file is automatically purged from
filesystem.

Automatic purge and deprecation jobs are done during dump creation.

Once created a dump can not be changed except for its ``deprecated`` field that can be
checked to manually deprecate dump but this is not reversible and a deprecated dump can
not be made available again.


Integrity
---------

You may need to check if a dump archive has been correctly downloaded and to do
so the dump stores a *BLAKE2* checksum that you can compare against your downloaded
file.

The `GNU Core Utilities <https://www.gnu.org/software/coreutils/>`_ (that is
installed on almost all non Windows systems) provides a command ``b2sum`` to compute a
`BLAKE2 checksum <https://www.gnu.org/savannah-checkouts/gnu/coreutils/manual/html_node/b2sum-invocation.html>`_
for a file: ::

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


Managing API keys
*****************

API key is for the futur feature of "API client" that would help to get and load a dump
directly from a command without to go to the admin to download it.

As for the dump object, API key have the same concept of automatic depreciation. This
may change a little when the API client feature will come.
