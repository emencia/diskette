from collections import Counter


def get_duplicates(items):
    """
    An efficient way to get a list of duplicated items.

    Arguments:
        items (list): A list of hashable items to check for duplicates. Non hashable
            items will raise an error.

    Returns:
        generator: A generator of duplicated items.
    """
    c = Counter()
    seen = set()

    for i in items:
        c[i] += 1

        if c[i] > 1 and i not in seen:
            seen.add(i)
            yield i
