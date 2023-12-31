import logging

import pytest

from diskette.core.abstracts import DumpCommandAbstract
from diskette.exceptions import DisketteError
from diskette.utils.loggers import LoggingOutput


@pytest.mark.parametrize("setting, arg, expected", [
    ("foo", None, "foo"),
    ("foo", "bar", "bar"),
    (None, "bar", "bar"),
])
def test_tarball_destination_valid(settings, setting, arg, expected):
    """
    Command properly discover the destination to use
    """
    commander = DumpCommandAbstract()
    commander.logger = LoggingOutput()

    settings.DISKETTE_DUMP_PATH = setting
    assert commander.get_tarball_destination(arg) == expected


def test_tarball_destination_invalid(settings):
    """
    Command should raise an error when resolved value for tarball destination is empty.
    """
    commander = DumpCommandAbstract()
    commander.logger = LoggingOutput()

    settings.DISKETTE_DUMP_PATH = None
    with pytest.raises(DisketteError) as excinfo:
        commander.get_tarball_destination("")

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
    commander = DumpCommandAbstract()
    commander.logger = LoggingOutput()

    # Dummy JSON source to open if needed
    json_source = tmp_path / "apps.json"
    json_source.write_text("{\"bar\": true}")

    settings.DISKETTE_APPS = setting

    # Patch source path argument if not empty, to fill it with dummy JSON Path instead
    if value and value == "apps.json":
        value = json_source

    assert commander.get_application_configurations(
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
    commander = DumpCommandAbstract()
    commander.logger = LoggingOutput()

    settings.DISKETTE_STORAGES = setting

    assert commander.get_storage_paths(value, disabled) == expected


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
    commander = DumpCommandAbstract()
    commander.logger = LoggingOutput()

    settings.DISKETTE_STORAGES_EXCLUDES = setting

    assert commander.get_storage_excludes(value, disabled) == expected


def test_dump(caplog, settings, db, tests_settings, tmp_path):
    """
    Dump method with the right arguments should correctly proceed to dump, archive
    everything and output some logs.
    """
    caplog.set_level(logging.DEBUG)

    storage_samples = tests_settings.fixtures_path / "storage_samples"

    commander = DumpCommandAbstract()
    commander.logger = LoggingOutput()

    tarball = commander.dump(
        tmp_path,
        no_data=False,
        no_storages=False,
        application_configurations=[
            ("Django auth", {"models": ["auth.group", "auth.user"]}),
            ("Django site", {"models": ["sites"]}),
        ],
        storages=[
            storage_samples / "storage-1",
            storage_samples / "storage-2"
        ],
        storages_basepath=storage_samples,
        storages_excludes=["foo/*"],
    )

    assert tarball.exists() is True

    assert caplog.record_tuples == [
        (
            "diskette",
            20,
            "=== Starting dump ==="
        ),
        (
            "diskette",
            10,
            "- Tarball will be written into: {}".format(tmp_path)
        ),
        (
            "diskette",
            10,
            "- Tarball filename pattern: diskette{features}.tar.gz"
        ),
        (
            "diskette",
            10,
            "- Data dump enabled for application:"
        ),
        (
            "diskette",
            10,
            "  ├── Django auth"
        ),
        (
            "diskette",
            10,
            "  └── Django site"
        ),
        (
            "diskette",
            10,
            "- Storage dump enabled for:"
        ),
        (
            "diskette",
            10,
            "  ├── {}/storage-1".format(storage_samples)
        ),
        (
            "diskette",
            10,
            "  └── {}/storage-2".format(storage_samples)
        ),
        (
            "diskette",
            10,
            "- Storage exclude patterns enabled:"
        ),
        (
            "diskette",
            10,
            "  └── foo/*"
        ),
        (
            "diskette",
            20,
            "Dumping data for application 'Django auth'"
        ),
        (
            "diskette",
            20,
            "Dumping data for application 'Django site'"
        ),
        (
            "diskette",
            20,
            "Appending data to the archive"
        ),
        (
            "diskette",
            20,
            "Appending storages to the archive"
        ),
        (
            "diskette",
            20,
            (
                "Dump tarball was created at: {}/diskette_data_storages.tar.gz".format(
                    tmp_path
                )
            )
        )
    ]
