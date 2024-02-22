import pytest

from diskette.utils.lists import unduplicated_merge_lists


@pytest.mark.parametrize("source, extra, expected", [
    ([], [], []),
    (["foo"], [], ["foo"]),
    ([], ["foo"], ["foo"]),
    (["foo"], ["bar"], ["foo", "bar"]),
    (["foo", "ping"], ["foo", "bar", "foo"], ["foo", "ping", "bar"]),
    # Method does not deduplicate items from source or extra themselves, only during
    # merging between them
    (["foo", "foo"], ["foo", "bar"], ["foo", "foo", "bar"]),
])
def test_unduplicated_merge_lists(source, extra, expected):
    """
    Merge should be correctly done without duplicated items.
    """
    assert unduplicated_merge_lists(source, extra) == expected
