from django.conf import settings


def is_url(path):
    """
    Determine if given path is an elligible URL or not.

    Value is assumed to be an URL if it is a string and it starts with an allowed
    network protocol (such as ``http://``) from setting
    ``DISKETTE_DOWNLOAD_ALLOWED_PROTOCOLS``.

    Arguments:
        path (object): Any kind of object type but only a string is recognized as a
            possible URL.

    Returns:
        boolean: True if recognized as an URL else False.
    """
    return (
        isinstance(path, str) and
        path.startswith(settings.DISKETTE_DOWNLOAD_ALLOWED_PROTOCOLS)
    )
