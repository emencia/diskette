from pathlib import Path


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

DISKETTE_DUMP_PATH = Path.cwd()
"""
For where are stored created dump.

This is not really important since the archive is meant to be deleted once extracted.
However you may want to write elsewhere so give it any valid path you want, this won't
impact the dump process.
"""

DISKETTE_DUMP_FILENAME = "diskette{features}.tar.gz"
"""
Filename for dump tarball file. It must ends with ``.tar.gz``. The pattern
``{features}`` is required if you want different files depending enable dump kind
(data, storages, all) else every dump kind will overwrite each other.

For a dump with data and storages it would be ``diskette_data_storages.tar.gz``.
"""

DISKETTE_LOAD_STORAGES_PATH = Path.cwd()
"""
For where to extract archive storages contents. On default this will be the current
working directory.
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
