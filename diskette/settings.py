
DISKETTE_APPS = []
"""
List of application definitions to dump their data.
"""

DISKETTE_STORAGES = []
"""
List of Path objects for storage to collect and dump.
"""

DISKETTE_STORAGES_EXCLUDES = []
"""
List of *Unix shell-style wildcards* patterns to filter out some storages files.

You may find more details on these pattern syntax in Python builtin module ``fnmatch``.
"""

DISKETTE_DUMP_PATH = None
"""
A ``pathlib.Path`` object for destination path where dumps will be created.

If value is empty Diskette will use the current working directory from the Python
execution.
"""

DISKETTE_DUMP_FILENAME = "diskette{features}.tar.gz"
"""
Filename for dump tarball file. It must ends with ``.tar.gz``. The pattern
``{features}`` is required if you want different filename depending enabled dump option
set (data, storages, everything) else every dump kind will overwrite each other.

For a dump with data and storages it would be ``diskette_data_storages.tar.gz``.
"""

DISKETTE_DUMP_AUTO_PURGE = True
"""
When this setting is true, a routine is executed to purge all deprecated dumps that
still have a file (in case of internal failures). This routine is only executed after
the end of a new created dump process.

If false, there won't be any purge and you will have either to delete each deprecated
dump or manually execute ``DumpFile.purge_deprecated_dumps()`` to remove deprecated
dump files.

.. Hint::
    The Django admin action to delete all selected objects from change list will
    correctly purge files so it can be a workaround.
"""

DISKETTE_LOAD_STORAGES_PATH = None
"""
A ``pathlib.Path`` object for where to extract archive storages contents from a dump.

If value is empty Diskette will use the current working directory from the Python
execution.

.. Warning::
    It must always be a parent directory of all your storages because a dump store the
    storages directories relatively to this setting.

    During dump, there is a check on storages content that will fails if some storages
    have different parent tree.

Commonly a project only define the media directory as a storage so for this
structure: ::

    /home/sample
    └── project
        └── medias
            ├── covers
            └── thumbs

You would have these settings: ::

    DISKETTE_STORAGES = ["/home/sample/project/medias"]
    DISKETTE_LOAD_STORAGES_PATH = "/home/sample/project"

But for more specific project where you would want to store things outside of project
like with this structure: ::

    .
    ├── important-data
    └── project
        └── medias
            ├── covers
            └── thumbs

You would have these settings: ::

    DISKETTE_STORAGES = [
        "/home/sample/important-data",
        "/home/sample/project/medias",
    ]
    DISKETTE_LOAD_STORAGES_PATH = "/home/sample"

"""

DISKETTE_LOAD_MINIMAL_FILESIZE = 6
"""
A data dump file size must be greater than this value to be loaded else it is ignored.
This limit value is defined in bytes.
"""

DISKETTE_DOWNLOAD_ALLOWED_PROTOCOLS = ("http://", "https://")
"""
A tuple or list of network protocols allowed to be used for downloading dump to load.
"""

DISKETTE_DOWNLOAD_ALLOW_REDIRECT = False
"""
Enable download requests to follow possible redirects. On default this is disabled, for
security you should always use the proper and direct URL.
"""

DISKETTE_DOWNLOAD_TIMEOUT = 10
"""
Time in seconds before a download request is assumed to timeout. On defaut it is set
to 10seconds.
"""

DISKETTE_DOWNLOAD_CHUNK = 8192
"""
Size in bytes of download chunk. You should not change this without to know exactly
what you are doing.
"""
