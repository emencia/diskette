import pytest

from diskette.exceptions import ApplicationRegistryError


def test_registry_errors_single_message():
    """
    With a single message string given, the exception just print out the message
    string.
    """
    with pytest.raises(ApplicationRegistryError) as excinfo:
        raise ApplicationRegistryError("Yo")

    assert str(excinfo.value) == "Yo"
    assert excinfo.value.get_payload_details() == []


def test_registry_errors_multiple_messages():
    """
    TODO
    """
    with pytest.raises(ApplicationRegistryError) as excinfo:
        raise ApplicationRegistryError(error_messages={
            "app1": "There is no way it would work",
            "app 2": "That's illegal syntax there sir",
        })

    assert str(excinfo.value) == "Some defined applications have errors: app1, app 2"
    assert excinfo.value.get_payload_details() == [
        "There is no way it would work",
        "That's illegal syntax there sir"
    ]
