
class BaseFileSizeAbstract:
    """
    Base abstract for classes which try to get a file size from a Path object.

    .. Notes::
        See ``mocked_dumper_filesize()`` from ``tests/conftest.py`` for reason about why
        this abstract exists.
    """
    def get_file_size(self, path):
        """
        Shortcut to get file size from a Path object.

        Arguments:
            path (pathlib.Path): File Path object.

        Returns:
            integer: Size of file.
        """
        return path.stat().st_size
