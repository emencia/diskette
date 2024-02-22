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


def unduplicated_merge_lists(source, extra):
    """
    Safely merge source and extra lists without duplicate items.

    Arguments:
        source (list): The base source list where to merge extra.
        extra (list):  The extra list to merge into base source.

    Returns:
        list: List that combine source and extra without duplicate items. In case of
            duplicate items in extra list the source one is keeped, so the sorting
            priority will be from source list.
    """
    merged = [v for v in source]
    merged.extend(v for v in extra if v not in source)

    return merged
