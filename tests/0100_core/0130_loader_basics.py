import json
import shutil

import pytest
from freezegun import freeze_time

from diskette.core.manager import DumpManager
from diskette.exceptions import DumpManagerError, ApplicationRegistryError

from tests.samples import SAMPLE_APPS


def test_validate_applications():
    """
    Application validation should raise an ApplicationRegistryError exception that
    contains detail messages for model errors.
    """
    manager = DumpManager([
        ("meh", {}),
        ("foo.bar", {"models": "bar", "excludes": "nope"}),
    ])
    with pytest.raises(ApplicationRegistryError) as excinfo:
        manager.validate_applications()

    assert str(excinfo.value) == (
        "Some defined applications have errors: meh, foo.bar"
    )
    assert excinfo.value.get_payload_details() == [
        "<ApplicationModel: meh>: 'models' must not be an empty value.",
        "<ApplicationModel: foo.bar>: 'excludes' argument must be a list.",
    ]
