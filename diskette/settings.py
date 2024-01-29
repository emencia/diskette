"""
Default application settings
----------------------------

These are the default settings you can override in your own project settings
right after the line which load the default app settings.

"""
from pathlib import Path


DISKETTE_APPS = []
"""
Application definition to dump data
"""

DISKETTE_STORAGES = []
"""
A list of Path objects for storage to collect and dump
"""

DISKETTE_STORAGES_EXCLUDES = []
"""
A list of *Unix shell-style wildcards* patterns to filter out some storages files.

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
"""

DISKETTE_LOAD_STORAGES_PATH = Path.cwd()
"""
For where to extract archive storages contents
"""
