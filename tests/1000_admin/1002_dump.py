from django.contrib.admin.sites import AdminSite

import pytest
from freezegun import freeze_time

from diskette.core.processes import post_dump_save_process
from diskette.factories import DumpFileFactory
from diskette.models import DumpFile
from diskette.admin import DumpFileAdmin
from diskette.forms import DumpFileAdminForm
from diskette.utils.tests import (
    get_admin_add_url, get_admin_change_url, get_admin_list_url,
    build_post_data_from_object,
)


def test_dump_admin_ping_add(db, admin_client):
    """
    DumpFile model admin add form view should not raise error on GET request.
    """
    url = get_admin_add_url(DumpFile)
    response = admin_client.get(url)

    assert response.status_code == 200


def test_dump_admin_ping_list(db, admin_client):
    """
    DumpFile model admin list view should not raise error on GET request.
    """
    url = get_admin_list_url(DumpFile)
    response = admin_client.get(url)

    assert response.status_code == 200


def test_dump_admin_ping_detail(db, admin_client):
    """
    DumpFile model admin detail view should not raise error on GET request.
    """
    obj = DumpFileFactory()

    url = get_admin_change_url(obj)
    response = admin_client.get(url)

    assert response.status_code == 200


@pytest.mark.parametrize("purge_enable, deprecated_exists", [
    (True, False),
    (False, True),
])
@freeze_time("2012-10-15 10:00:00")
def test_dump_process(db, admin_client, rf, settings, tmp_path, purge_enable,
                      deprecated_exists):
    """
    Process function should only care about created and non deprecated dump then
    possibly purge deprecated dump depending value of setting
    'DISKETTE_DUMP_AUTO_PURGE'.
    """
    settings.DISKETTE_DUMP_AUTO_PURGE = purge_enable

    # Define dump destination dir and some app data to dump
    settings.DISKETTE_DUMP_PATH = tmp_path
    settings.DISKETTE_APPS = [
        [
            "django.contrib.sites", {
                "comments": "django.contrib.sites",
                "natural_foreign": True,
                "models": "sites"
            }
        ],
    ]

    # Expected dump destination file path
    expected_destination = tmp_path / "diskette_2012-10-15T100000.tar.gz"

    # Dump with other status than 'created' should not proceed to dump anything
    dump = DumpFileFactory(status=10)
    post_dump_save_process(dump)
    assert dump.path == ""
    assert expected_destination.exists() is False

    # Deprecated dump should not proceed to dump anything
    dump = DumpFileFactory(deprecated=True)
    post_dump_save_process(dump)
    assert dump.path == ""
    assert expected_destination.exists() is False

    # Create a fake deprecated dump with a file to purge
    dummy_dump = tmp_path / "dummy_dump.txt"
    dummy_dump.write_text("Yolo")
    DumpFileFactory(deprecated=True, path=str(dummy_dump))
    assert dummy_dump.exists() is True

    # Proceed to a data only dump
    dump = DumpFileFactory(with_data=True, with_storage=False)
    post_dump_save_process(dump)
    assert expected_destination.exists() is True

    assert DumpFile.objects.filter(
        deprecated=False, with_data=True, with_storage=False
    ).count() == 1
    assert dummy_dump.exists() is deprecated_exists


@freeze_time("2012-10-15 10:00:00")
def test_dump_admin_creation_process(db, admin_client, rf, settings, tmp_path):
    """
    Creating a dump from admin will trigger the dump process that should correctly
    dump data into an archive.

    This does not test really through admin view instead we reproduce the same admin
    form view mechanic just we don't go through real requests.
    """
    # Define dump destination dir and some app data to dump
    settings.DISKETTE_DUMP_PATH = tmp_path
    settings.DISKETTE_APPS = [
        [
            "django.contrib.sites", {
                "comments": "django.contrib.sites",
                "natural_foreign": True,
                "models": "sites"
            }
        ],
    ]

    # Expected dump destination file path
    expected_destination = tmp_path / "diskette_2012-10-15T100000.tar.gz"

    # Build POST for a dump with data only
    data = build_post_data_from_object(
        DumpFile,
        DumpFileFactory.build(with_storage=False),
        ignore=["id"]
    )
    # Submit POST to form and save object
    f = DumpFileAdminForm(data)
    assert f.is_valid() is True
    created = f.save()

    # Build admin view instance to call the save_model method responsible of executing
    # the dump process created from form
    my_model_admin = DumpFileAdmin(model=DumpFile, admin_site=AdminSite())
    my_model_admin.save_model(
        obj=created, request=rf, form=f, change=False
    )

    assert DumpFile.objects.filter(path=expected_destination.name).count() == 1
    assert expected_destination.exists() is True
