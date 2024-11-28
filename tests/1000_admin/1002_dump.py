from django.contrib.admin.sites import AdminSite
from django.urls import reverse

import pytest
from freezegun import freeze_time

from diskette.core.processes import post_dump_save_process
from diskette.factories import DumpFileFactory
from diskette.models import DumpFile
from diskette.admin import DumpFileAdmin
from diskette.forms import DumpFileAdminForm
from diskette.utils.tests import (
    get_admin_add_url, get_admin_change_url, get_admin_list_url,
    build_post_data_from_object, html_pyquery,
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
def test_dump_process(db, settings, tmp_path, purge_enable, deprecated_exists):
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
def test_dump_admin_creation_process(db, rf, settings, tmp_path):
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


def test_dump_admin_download_deprecated(db, admin_client, settings, tmp_path):
    """
    Deprecated dump won't have any link to download and the download view should
    return a 404 status.
    """
    settings.SENDFILE_ROOT = tmp_path
    settings.DISKETTE_DUMP_PATH = settings.SENDFILE_ROOT

    # Create a deprecated dump with a dummy file
    dummy_dump = tmp_path / "dummy_dump.txt"
    dummy_dump.write_text("Nope")
    dummy = DumpFileFactory(deprecated=True, path=str(dummy_dump))

    # No link for deprecated
    response = admin_client.get(get_admin_change_url(dummy))
    assert response.status_code == 200
    dom = html_pyquery(response)
    assert dom.find(".field-path_url a") == []

    # Even trying to directly request the download view for this dump would lead to
    # a 404 response because deprecated dump are excluded from view queryset
    url = reverse("admin:diskette_admin_dump_download", args=[dummy.id])
    download_response = admin_client.get(url)
    assert download_response.status_code == 404


def test_dump_admin_download_empty(db, admin_client, settings, tmp_path):
    """
    Dump with an empty path won't have any link to download and the download view
    should return a 404 status.
    """
    settings.SENDFILE_ROOT = tmp_path
    settings.DISKETTE_DUMP_PATH = settings.SENDFILE_ROOT

    # Create a deprecated dump with a dummy file
    dummy = DumpFileFactory(deprecated=False)

    # No link for deprecated
    response = admin_client.get(get_admin_change_url(dummy))
    assert response.status_code == 200
    dom = html_pyquery(response)
    assert dom.find(".field-path_url a") == []

    # Even trying to directly request the download view for this dump would lead to
    # a 404 response because deprecated dump are excluded from view queryset
    url = reverse("admin:diskette_admin_dump_download", args=[dummy.id])
    download_response = admin_client.get(url)
    assert download_response.status_code == 404


def test_dump_admin_download_purged(db, admin_client, settings, tmp_path):
    """
    Dump with a purged path won't have any link to download and the download view
    should return a 404 status.
    """
    settings.SENDFILE_ROOT = tmp_path
    settings.DISKETTE_DUMP_PATH = settings.SENDFILE_ROOT

    # Create a deprecated dump with a dummy file
    dummy = DumpFileFactory(deprecated=False, path="removed://foo.txt")

    # No link for deprecated
    response = admin_client.get(get_admin_change_url(dummy))
    assert response.status_code == 200
    dom = html_pyquery(response)
    assert dom.find(".field-path_url a") == []

    # Even trying to directly request the download view for this dump would lead to
    # a 404 response because deprecated dump are excluded from view queryset
    url = reverse("admin:diskette_admin_dump_download", args=[dummy.id])
    download_response = admin_client.get(url)
    assert download_response.status_code == 404


def test_dump_admin_download_available(db, client, admin_client, settings, tmp_path):
    """
    Available dump should display a download link that is restricted to staff users.
    """
    settings.SENDFILE_ROOT = tmp_path
    settings.DISKETTE_DUMP_PATH = settings.SENDFILE_ROOT

    # Create an available dump with a dummy file
    available_dump = tmp_path / "available_dump.txt"
    available_dump.write_text("Yolo")
    available = DumpFileFactory(deprecated=False, path=str(available_dump))
    assert available_dump.exists() is True

    # Link is present for available dump
    response = admin_client.get(get_admin_change_url(available))
    assert response.status_code == 200

    # Link return the file content to download
    dom = html_pyquery(response)
    file_url = dom.find(".field-path_url a")[0].get("href")
    download_response = admin_client.get(file_url)
    assert download_response.status_code == 200
    assert download_response.content == b"Yolo"

    # Download link is only reachable from staff user, lambda user are redirected to
    # admin login view to authenticate with a proper staff account
    download_response = client.get(file_url, follow=True)
    assert download_response.redirect_chain == [
        ("/admin/login/?next={}".format(file_url), 302)
    ]
    assert download_response.status_code == 200
