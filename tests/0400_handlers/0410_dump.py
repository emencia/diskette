import logging

import pytest

from django.template.defaultfilters import filesizeformat

from diskette.core.handlers import DumpCommandHandler
from diskette.exceptions import DisketteError
from diskette.utils.loggers import LoggingOutput


@pytest.mark.parametrize("setting, arg, expected", [
    ("foo", None, "foo"),
    ("foo", "bar", "bar"),
    (None, "bar", "bar"),
])
def test_archive_destination_valid(settings, setting, arg, expected):
    """
    Command properly discover the destination to use
    """
    handler = DumpCommandHandler()
    handler.logger = LoggingOutput()

    settings.DISKETTE_DUMP_PATH = setting
    assert handler.get_archive_destination(arg) == expected


def test_archive_destination_invalid(settings):
    """
    Command should raise an error when resolved value for archive destination is empty.
    """
    handler = DumpCommandHandler()
    handler.logger = LoggingOutput()

    settings.DISKETTE_DUMP_PATH = None
    with pytest.raises(DisketteError) as excinfo:
        handler.get_archive_destination("")

    assert str(excinfo.value) == "Destination path can not be an empty value"


@pytest.mark.parametrize("setting, value, disabled, expected", [
    # No values
    ([], None, False, (False, [])),
    # From settings only
    (["foo"], None, False, (True, ["foo"])),
    # From settings but disabled
    (["foo"], None, True, (False, [])),
    # From argument with JSON file
    (["foo"], "apps.json", False, (True, {"bar": True})),
    # From settings and argument with JSON file
    (["foo"], "apps.json", False, (True, {"bar": True})),
    # From settings and with JSON string
    (["foo"], "{\"bar\": true}", False, (True, {"bar": True})),
    # From settings and with Python list
    (["foo"], ["bar"], False, (True, ["bar"])),
    # From settings and argument but disabled
    (["foo"], "apps.json", True, (False, [])),
])
def test_application_configurations(settings, tmp_path, setting, value, disabled,
                                    expected):
    """
    Application configurations should be correctly discovered from either settings or
    argument.
    """
    handler = DumpCommandHandler()
    handler.logger = LoggingOutput()

    # Dummy JSON source to open if needed
    json_source = tmp_path / "apps.json"
    json_source.write_text("{\"bar\": true}")

    settings.DISKETTE_APPS = setting

    # Patch source path argument if not empty, to fill it with dummy JSON Path instead
    if value and value == "apps.json":
        value = json_source

    assert handler.get_application_configurations(
        appconfs=value,
        no_data=disabled
    ) == expected


@pytest.mark.parametrize("setting, value, disabled, expected", [
    # No values
    ([], None, False, (False, [])),
    # From settings only
    (["foo"], None, False, (True, ["foo"])),
    # From settings and argument
    (["foo"], ["bar"], False, (True, ["bar"])),
    # From settings but disabled
    (["foo"], None, True, (False, [])),
    # From settings and argument but disabled
    (["foo"], ["bar"], True, (False, [])),
])
def test_storage_paths(settings, tmp_path, setting, value, disabled, expected):
    """
    Storage paths should be correctly discovered from either settings or argument.
    """
    handler = DumpCommandHandler()
    handler.logger = LoggingOutput()

    settings.DISKETTE_STORAGES = setting

    assert handler.get_storage_paths(value, disabled) == expected


@pytest.mark.parametrize("setting, value, disabled, expected", [
    # No values
    ([], None, False, (False, [])),
    # From settings only
    (["foo"], None, False, (True, ["foo"])),
    # From settings and argument
    (["foo"], ["bar"], False, (True, ["bar"])),
    # From settings but disabled
    (["foo"], None, True, (False, [])),
    # From settings and argument but disabled
    (["foo"], ["bar"], True, (False, [])),
])
def test_storage_excludes(settings, tmp_path, setting, value, disabled, expected):
    """
    Storage excluding patterns should be correctly discovered from either settings or
    argument.
    """
    handler = DumpCommandHandler()
    handler.logger = LoggingOutput()

    settings.DISKETTE_STORAGES_EXCLUDES = setting

    assert handler.get_storage_excludes(value, disabled) == expected


def test_dump(caplog, settings, db, mocked_checksum, tests_settings, tmp_path):
    """
    Dump method with the right arguments should correctly proceed to dump, archive
    everything and output some logs.
    """
    caplog.set_level(logging.DEBUG)

    storage_samples = tests_settings.fixtures_path / "storage_samples"
    storage_1 = storage_samples / "storage-1"
    storage_2 = storage_samples / "storage-2"

    handler = DumpCommandHandler()
    handler.logger = LoggingOutput()

    archive = handler.dump(
        tmp_path,
        no_data=False,
        no_storages=False,
        application_configurations=[
            ("Django auth", {"models": ["auth.Group", "auth.User"]}),
            ("Django site", {"models": ["sites"]}),
        ],
        storages=[storage_1, storage_2],
        storages_basepath=storage_samples,
        storages_excludes=["foo/*"],
    )

    assert archive.exists() is True

    # Flatten logging messages
    logs = [
        name + ":" + str(lv) + ":" + msg
        for name, lv, msg in caplog.record_tuples
    ]

    assert logs == [
        "diskette:20:=== Starting dump ===",
        "diskette:10:- Tarball will be written into: {}".format(tmp_path),
        "diskette:10:- Tarball filename pattern: diskette{features}.tar.gz",
        "diskette:10:- Data dump enabled for application:",
        "diskette:10:  ├── Django auth",
        "diskette:10:  └── Django site",
        "diskette:10:- Storage dump enabled for:",
        "diskette:10:  ├── {}".format(storage_1),
        "diskette:10:  └── {}".format(storage_2),
        "diskette:10:- Storage exclude patterns enabled:",
        "diskette:10:  └── foo/*",
        "diskette:20:Dumping data for application 'Django auth'",
        "diskette:10:- Including: auth.Group, auth.User",
        (
            "diskette:10:- Excluding: auth.Permission, auth.Group_permissions, "
            "auth.User_groups, auth.User_user_permissions"
        ),
        "diskette:10:- Written file: django-auth.json (2 bytes)",
        "diskette:20:Dumping data for application 'Django site'",
        "diskette:10:- Including: sites.Site",
        "diskette:10:- Written file: django-site.json (94 bytes)",
        "diskette:20:Appending data to the archive",
        "diskette:20:Appending storages to the archive",
        "diskette:10:- storage-1/blue.png (1.5 KB)",
        "diskette:10:- storage-1/sample.txt (11 bytes)",
        "diskette:10:- storage-1/plop/green.png (1.6 KB)",
        "diskette:10:- storage-2/pong/sample.nope (11 bytes)",
        "diskette:10:- storage-2/ping/grey.png (1.6 KB)",
        "diskette:20:Dump archive was created at: {} (3.7 KB)".format(archive),
        "diskette:20:Checksum: dummy-checksum",
    ]


@pytest.mark.parametrize("options, expected", [
    (
        {
            "no_data": False,
            "no_storages": False,
        },
        [
            "diskette:20:=== Starting dump ===",
            "diskette:10:- Tarball will be written into: {tmp_path}",
            "diskette:10:- Tarball filename pattern: diskette{{features}}.tar.gz",
            "diskette:10:- Data dump enabled for application:",
            "diskette:10:  ├── Django auth",
            "diskette:10:  └── Django site",
            "diskette:10:- Storage dump enabled for:",
            "diskette:10:  ├── {storage_1}",
            "diskette:10:  └── {storage_2}",
            "diskette:10:- Storage exclude patterns enabled:",
            "diskette:10:  └── foo/*",
            "diskette:20:Dumping data for application 'Django auth'",
            "diskette:10:- Including: auth.Group, auth.User",
            (
                "diskette:10:- Excluding: auth.Permission, auth.Group_permissions, "
                "auth.User_groups, auth.User_user_permissions"
            ),
            "diskette:10:- Written file: django-auth.json (2 bytes)",
            "diskette:20:Dumping data for application 'Django site'",
            "diskette:10:- Including: sites.Site",
            "diskette:10:- Written file: django-site.json (94 bytes)",
            "diskette:20:Appending data to the archive",
            "diskette:20:Appending storages to the archive",
            "diskette:10:- storage-1/blue.png (1.5 KB)",
            "diskette:10:- storage-1/sample.txt (11 bytes)",
            "diskette:10:- storage-1/plop/green.png (1.6 KB)",
            "diskette:10:- storage-2/pong/sample.nope (11 bytes)",
            "diskette:10:- storage-2/ping/grey.png (1.6 KB)",
            "diskette:20:Dump archive was created at: {archive} (3.7 KB)",
            "diskette:20:Checksum: dummy-checksum",
        ]
    ),
    (
        {
            "no_data": False,
            "no_storages": False,
            "no_checksum": True,
        },
        [
            "diskette:20:=== Starting dump ===",
            "diskette:10:- Tarball will be written into: {tmp_path}",
            "diskette:10:- Tarball filename pattern: diskette{{features}}.tar.gz",
            "diskette:10:- Data dump enabled for application:",
            "diskette:10:  ├── Django auth",
            "diskette:10:  └── Django site",
            "diskette:10:- Storage dump enabled for:",
            "diskette:10:  ├── {storage_1}",
            "diskette:10:  └── {storage_2}",
            "diskette:10:- Storage exclude patterns enabled:",
            "diskette:10:  └── foo/*",
            "diskette:20:Dumping data for application 'Django auth'",
            "diskette:10:- Including: auth.Group, auth.User",
            (
                "diskette:10:- Excluding: auth.Permission, auth.Group_permissions, "
                "auth.User_groups, auth.User_user_permissions"
            ),
            "diskette:10:- Written file: django-auth.json (2 bytes)",
            "diskette:20:Dumping data for application 'Django site'",
            "diskette:10:- Including: sites.Site",
            "diskette:10:- Written file: django-site.json (94 bytes)",
            "diskette:20:Appending data to the archive",
            "diskette:20:Appending storages to the archive",
            "diskette:10:- storage-1/blue.png (1.5 KB)",
            "diskette:10:- storage-1/sample.txt (11 bytes)",
            "diskette:10:- storage-1/plop/green.png (1.6 KB)",
            "diskette:10:- storage-2/pong/sample.nope (11 bytes)",
            "diskette:10:- storage-2/ping/grey.png (1.6 KB)",
            "diskette:20:Dump archive was created at: {archive} (3.7 KB)",
        ]
    ),
    (
        {
            "no_data": True,
            "no_storages": False,
        },
        [
            "diskette:20:=== Starting dump ===",
            "diskette:10:- Tarball will be written into: {tmp_path}",
            "diskette:10:- Tarball filename pattern: diskette{{features}}.tar.gz",
            "diskette:10:- Data dump is disabled",
            "diskette:10:- Storage dump enabled for:",
            "diskette:10:  ├── {storage_1}",
            "diskette:10:  └── {storage_2}",
            "diskette:10:- Storage exclude patterns enabled:",
            "diskette:10:  └── foo/*",
            "diskette:20:Appending storages to the archive",
            "diskette:10:- storage-1/blue.png (1.5 KB)",
            "diskette:10:- storage-1/sample.txt (11 bytes)",
            "diskette:10:- storage-1/plop/green.png (1.6 KB)",
            "diskette:10:- storage-2/pong/sample.nope (11 bytes)",
            "diskette:10:- storage-2/ping/grey.png (1.6 KB)",
            "diskette:20:Dump archive was created at: {archive} (3.5 KB)",
            "diskette:20:Checksum: dummy-checksum",
        ]
    ),
    (
        {
            "no_data": False,
            "no_storages": True,
        },
        [
            "diskette:20:=== Starting dump ===",
            "diskette:10:- Tarball will be written into: {tmp_path}",
            "diskette:10:- Tarball filename pattern: diskette{{features}}.tar.gz",
            "diskette:10:- Data dump enabled for application:",
            "diskette:10:  ├── Django auth",
            "diskette:10:  └── Django site",
            "diskette:10:- Storage dump is disabled",
            "diskette:20:Dumping data for application 'Django auth'",
            "diskette:10:- Including: auth.Group, auth.User",
            (
                "diskette:10:- Excluding: auth.Permission, auth.Group_permissions, "
                "auth.User_groups, auth.User_user_permissions"
            ),
            "diskette:10:- Written file: django-auth.json (2 bytes)",
            "diskette:20:Dumping data for application 'Django site'",
            "diskette:10:- Including: sites.Site",
            "diskette:10:- Written file: django-site.json (94 bytes)",
            "diskette:20:Appending data to the archive",
            "diskette:20:Dump archive was created at: {archive} ({size})",
            "diskette:20:Checksum: dummy-checksum",
        ]
    ),
])
def test_dump_options(caplog, settings, db, mocked_checksum, tests_settings, tmp_path,
                      options, expected):
    """
    Dump method with the right arguments should correctly proceed to dump, archive
    everything and output some logs.
    """
    caplog.set_level(logging.DEBUG)

    storage_samples = tests_settings.fixtures_path / "storage_samples"
    storage_1 = storage_samples / "storage-1"
    storage_2 = storage_samples / "storage-2"

    handler = DumpCommandHandler()
    handler.logger = LoggingOutput()

    archive = handler.dump(
        tmp_path,
        application_configurations=[
            ("Django auth", {"models": ["auth.Group", "auth.User"]}),
            ("Django site", {"models": ["sites"]}),
        ],
        storages=[storage_1, storage_2],
        storages_basepath=storage_samples,
        storages_excludes=["foo/*"],
        **options
    )

    assert archive.exists() is True

    # Flatten logging messages
    logs = [
        name + ":" + str(lv) + ":" + msg
        for name, lv, msg in caplog.record_tuples
    ]

    assert logs == [
        # Add possible 'tmp_path' in case it is used
        item.format(
            tmp_path=tmp_path,
            storage_1=storage_1,
            storage_2=storage_2,
            archive=archive,
            size=filesizeformat(archive.stat().st_size),
        )
        for item in expected
    ]
