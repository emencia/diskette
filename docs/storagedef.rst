.. _storagedef_intro:

==================
Storage definition
==================

A storage definition just defines a directory path to store in the archive.

The path can only be a directory, if you defines a file path it will raise an error
during dump.

Deployment
**********

When storages are deployed with the load command, they are uncompressed from archive
into a temporary directory. Each storage directory is then moved to its destination in
the basepath from setting ``DISKETTE_LOAD_STORAGES_PATH``.

If the basepath already contains a directory with the same name than a storage directory
it will be deleted before to be replaced with the storage from the archive.

Storage tree
************

Each storage directory is stored in archive relatively to the path from setting
``DISKETTE_LOAD_STORAGES_PATH`` so this setting should always be a parent directory
(direct or not) of all storage directories.

And obviously each storage path must start with the path from
``DISKETTE_LOAD_STORAGES_PATH``.

For example with these settings: ::

    DISKETTE_STORAGES = ["/home/sample/medias/covers"]
    DISKETTE_LOAD_STORAGES_PATH = "/home/sample/project"

The dump process will fail because ``/home/sample/medias/covers`` is not a child of
``/home/sample/project``, they are only siblings.


Simpliest sample
****************

Commonly a project only define the media directory as a storage so for this
structure: ::

    /home/sample
    └── project
        └── medias
            ├── covers
            └── thumbs

You would define these settings: ::

    DISKETTE_STORAGES = ["/home/sample/project/medias"]
    DISKETTE_LOAD_STORAGES_PATH = "/home/sample/project"


Granular sample
***************

You may have some media directory that are unwanted without using exclusion patterns.
Like with the following structure: ::

    /home/sample
    └── project
        └── medias
            ├── downloads
            ├── covers
            └── thumbs

Where ``/home/sample/project/downloads`` is unwanted for some reasons. If so you would
define these settings: ::

    DISKETTE_STORAGES = [
        "/home/sample/project/medias/covers",
        "/home/sample/project/medias/thumbs",
    ]
    DISKETTE_LOAD_STORAGES_PATH = "/home/sample/project"


Advanced sample
***************

For a more specific project, you may need to store things that are outside of
project directory like with this structure: ::

    /home/sample
    ├── important-data
    └── project
        └── medias
            ├── covers
            └── thumbs

You would define these settings: ::

    DISKETTE_STORAGES = [
        "/home/sample/important-data",
        "/home/sample/project/medias",
    ]
    DISKETTE_LOAD_STORAGES_PATH = "/home/sample"

.. Note::
    We recommend to avoid this structure kind because it allows to store and restore
    content outside of the project itself that can be a security issue or may overwrite
    your system.
