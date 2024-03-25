.. _tips_intro:


Tips
****

.. Caution::
    This document is a draft from some development notes. They may not be well written
    or contain some errors.


Storage deployment
------------------

Currently the storage directories are archived with relative path deducted from their
path minus the ``storages_basepath`` value (optionnally given to manager or default to
CWD path).

This implies that all storages are children path of ``storages_basepath``, else it is
an error. This is because we use ``storages_basepath`` to make relative path of a
storage path, since we do not allow for absolute directories (to avoid catastrophic
issue and prevent some malicious attacks).


About required freespace size
-----------------------------

Short version: you commonly need twice size of your content (data and storages).

Diskette create or use tarball with a "two slots" way, this is quicker and use less
memory but in returns it needs a filesystem which have at least twice size of the
tarball.

If you got a lot of data, you may need 2.5 size or more of the tarball, since in
archive the data are compressed but once extracted they recover their uncompressed size
until they are removed when imported in database.

Storage files are commonly binary files (image, video, pdf, etc..) so their size won't
really change once extracted.


About data integrity
--------------------

Did tried to test Diskette dump and load on some large project and finished on failure
because the production db contains permissions that don't exists anymore. Since Django
permissions are not really loadable, we can't restore the previous migration which
include the remove ones. But a single user has all permissions assigned included the
unexisting one, so loaddata fail on this user because it relies on data that do not
exists anymore.


Contenttype and permissions fix
...............................

A Django builtin command helps to purge stale content type and related object for when
applications have been removed but still related in some object relying on permissions
or directly content type: ::

    django-admin remove_stale_contenttypes --include-stale-apps

For example, if application *Blog* has been installed in project version 0.1.0. Then
Blog permissions have been assigned to an admin user. Now on project version 1.0.0,
Blog is removed. If you dump the user data, Django won't be able to load it because
an user has relation to unexisting Blog permissions.

.. Note::
    Permission objects are created automatically from Django migrations, we can't dump
    and load them.

This is because when the data are dumped the permissions still exists but when dump are
loaded the database is rebooted so Blog permissions won't exists anymore. Finally the
loading will fail because there are relations to unexisting permissions.

For this specific case (objects related to missing Contenttype or Permission), the
described command should fix problems.


DjangoCMS plugins
-----------------

All CMS plugins must be configured to be dumped after DjangoCMS dump. These plugins
may work even they are enabled before CMS but the Django serializer will fail to load
them.
