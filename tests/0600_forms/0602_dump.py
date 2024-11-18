from diskette.factories import DumpFileFactory
from diskette.models import DumpFile
from diskette.forms import DumpFileAdminForm
from diskette.utils.tests import compact_form_errors, build_post_data_from_object


def test_dump_form_creation(db):
    """
    Dump creation form just create the dump object and does not process the dump itself.
    """
    # Build initial POST data
    data = build_post_data_from_object(
        DumpFile,
        DumpFileFactory.build(with_storage=False),
        ignore=["id"]
    )

    f = DumpFileAdminForm(data)
    assert f.is_valid() is True
    assert compact_form_errors(f) == {}

    created = f.save()
    assert DumpFile.objects.all().count() == 1
    assert created.status == 0
    assert created.size == 0
    assert created.with_data is True
    assert created.with_storage is False
    assert created.path == ""


def test_dump_form_frozen_option_set(db):
    """
    Once dump object has been created, the option set is definitively frozen.
    """
    # Build initial POST data
    data = build_post_data_from_object(
        DumpFile,
        DumpFileFactory.build(with_storage=False),
        ignore=["id"]
    )

    f = DumpFileAdminForm(data)
    assert f.is_valid() is True
    created = f.save()
    assert DumpFile.objects.all().count() == 1
    assert created.with_data is True
    assert created.with_storage is False

    # Deprecated key can not be made available anymore
    data = build_post_data_from_object(DumpFile, created, ignore=["id", "key"])
    data["with_data"] = False
    data["with_storage"] = True
    f = DumpFileAdminForm(data, instance=created)
    # NOTE: No validation error is raised since the change form disable option set
    # fields
    assert f.is_valid() is True
    created.refresh_from_db()
    assert created.deprecated is False
    assert created.with_data is True
    assert created.with_storage is False


def test_dump_form_save_auto_deprecation(db):
    """
    Form save method will deprecate all identical option set.
    """
    # Create some non deprecated dumps
    DumpFileFactory(with_data=True, with_storage=True)
    DumpFileFactory(with_data=False, with_storage=True)
    # Multiple available identical set options for data only
    DumpFileFactory(with_data=True, with_storage=False)
    DumpFileFactory(with_data=True, with_storage=False)
    assert DumpFile.objects.filter(deprecated=False).count() == 4

    # Build initial POST data
    data = build_post_data_from_object(
        DumpFile,
        DumpFileFactory.build(with_data=True, with_storage=False),
        ignore=["id"]
    )

    f = DumpFileAdminForm(data)
    assert f.is_valid() is True
    assert compact_form_errors(f) == {}

    created = f.save()
    assert created.deprecated is False
    assert DumpFile.objects.all().count() == 5
    # Previous dump with identical options has been deprecated from 'form.save()'
    assert DumpFile.objects.filter(
        deprecated=False,
        with_data=True,
        with_storage=False
    ).count() == 1
