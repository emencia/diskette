# from pathlib import Path

# import pytest
from freezegun import freeze_time

# from django.core.exceptions import ValidationError
# from django.db.utils import IntegrityError

from diskette.factories import DumpFileFactory
from diskette.models import DumpFile


@freeze_time("2012-10-15 10:00:00")
def test_dump_basic(db):
    """
    Basic model validation with required fields should not fail.
    """
    dump = DumpFile()
    dump.full_clean()
    dump.save()
    assert dump.with_data is True
    assert dump.with_storage is True
    assert dump.deprecated is False
    assert str(dump) == "2012-10-15T10:00:00+00:00"
    assert DumpFile.objects.all().count() == 1


@freeze_time("2012-10-15 10:00:00")
def test_dump_creation(db):
    """
    Factory should correctly create a new object without any errors.
    """
    dump = DumpFileFactory()
    assert dump.with_data is True
    assert dump.with_storage is True
    assert dump.deprecated is False
    assert str(dump) == "2012-10-15T10:00:00+00:00"
    assert DumpFile.objects.all().count() == 1


def test_dump_purge_file(db, tmp_path):
    """
    Method 'DumpFile.purge_file()' should delete file and prefix path value.
    """
    dump_file = tmp_path / "foo.txt"
    dump_file.write_text("Dummy")

    dump = DumpFileFactory(path=str(dump_file))
    assert dump_file.exists() is True
    assert dump.path == str(dump_file)
    assert DumpFile.objects.all().count() == 1

    dump.purge_file()
    assert dump_file.exists() is False
    assert dump.path == "removed:/" + str(dump_file)


def test_dump_delete(db, tmp_path):
    """
    Method 'DumpFile.delete()' should delete file just after deleting object.
    """
    dump_file = tmp_path / "foo.txt"
    dump_file.write_text("Dummy")

    dump = DumpFileFactory(path=str(dump_file))
    assert dump_file.exists() is True
    assert dump.path == str(dump_file)
    assert DumpFile.objects.all().count() == 1

    dump.delete()
    assert dump_file.exists() is False
    assert DumpFile.objects.all().count() == 0


def test_dump_purge_deprecated_dumps(db, tmp_path):
    """
    Class method 'DumpFile.purge_deprecated_dumps()' should delete files from deprecated
    objects and should prefix their path.
    """
    dump1 = tmp_path / "dummy1.txt"
    dump1.write_text("Dummy 1")

    dump2 = tmp_path / "dummy2.txt"
    dump2.write_text("Dummy 2")

    dump3 = tmp_path / "dummy3.txt"
    dump3.write_text("Dummy 3")

    DumpFileFactory(path=str(dump1))
    DumpFileFactory(path=str(dump2), deprecated=True)
    DumpFileFactory(path=str(dump3))
    assert DumpFile.objects.all().count() == 3

    DumpFile.purge_deprecated_dumps()
    assert dump1.exists() is True
    assert dump2.exists() is False
    assert dump3.exists() is True
    assert DumpFile.objects.all().count() == 3
    assert DumpFile.objects.exclude(path__startswith="removed:/").count() == 2
