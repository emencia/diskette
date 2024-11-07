.. _tips_intro:


Tips
****


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


Integrity error on missing foreignkey
-------------------------------------

If an application dump loading process fails on a short message without more details
like: ::

    Integrity error: ForeignKey missing

Then this Diskette application definition is probably missing a model which is used
as a foreign relation from one of application models.

This is commonly the case if:

* You explicitely define app models and forgotten a model or a new one has been added
  after an application upgrade;
* You are explicitely excluding an app model that is required from another one;


About data integrity
--------------------

Some specific relation systems like with Django permissions can lead to unexpected
failures between two installations.

In fact Django permissions can not really be loaded since they are mostly initialized
through model migrations, they already exist in database before Diskette can load data.

However permissions are not cleared by Django automatically, developers need to perform
permissions cleaning themselves. It means a production database can contains stale
permissions. This is especially annoying with other model objects which rely
directly on permissions since these object will be dumped with relation to permissions.

Then if you try to load these dumps in another installation where the stale permissions
do not exist anymore, the dump will fail.

See below for a solution to resolve this situation.


Contenttype and permissions fix
...............................

A Django builtin command helps to purge stale content type and related object for when
applications have been removed but still related in some object relying on permissions
or directly content type: ::

    django-admin remove_stale_contenttypes --include-stale-apps

For example, an application *Blog* has been installed in project version 0.1.0 and
some Blog permissions have been assigned to an user. Then on project version 1.0.0,
Blog has been removed. If you dump the user data, Django won't be able to load the user
dump because it includes some relations to unexisting Blog permissions.

.. Note::
    Permission objects are created automatically from Django migrations, we can dump
    them but we can not load them. And Django Contenttypes will behave identically.

This is because when the data are dumped the permissions still exists but when dump are
loaded the database is rebooted so Blog permissions won't exists anymore. Finally the
loading will fail because there are relations to unexisting permissions.

For this specific case (objects related to missing Contenttype or Permission), the
described command should fix problems.


Applications plugins
--------------------

Some applications may allow to connect other applications as *plugins*, meaning the
application plugin depends on another one like DjangoCMS and its plugin system.

These applications plugins must be configured to be dumped after their parent
application dumps. If you don't follow this rule the dump process will work flawlessly
but loading will fail, commonly because of foreign keys.
