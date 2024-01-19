import os


def directory_size(path):
    """
    Recursively compute size of directory files.

    This won't compute the size of directories themselves.

    Returns:
        integer: The total size in bytes.
    """
    total = 0

    for entry in os.scandir(path):
        if os.path.exists(entry.path):
            if entry.is_file():
                total += entry.stat().st_size
            elif entry.is_dir():
                total += entry.stat().st_size
                total += directory_size(entry.path)

    return total
