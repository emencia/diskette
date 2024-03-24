import hashlib


def file_checksum(filepath):
    """
    Checksum a file in an efficient way for large files with blake2b.

    Borrowed from: https://stackoverflow.com/a/44873382

    Arguments:
        filepath (pathlib.Path): File path to open and checksum.

    Returns:
        string: The file checksum as 40 characters.
    """
    h = hashlib.blake2b()
    b = bytearray(128 * 1024)
    mv = memoryview(b)

    with open(filepath, "rb", buffering=0) as f:
        for n in iter(lambda: f.readinto(mv), 0):
            h.update(mv[:n])

    return h.hexdigest()
