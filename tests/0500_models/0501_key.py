from diskette.factories import APIkeyFactory
from diskette.models import APIkey


def test_key_basic(db):
    """
    Basic model validation with required fields should not fail.
    """
    key = APIkey()
    key.full_clean()
    key.save()
    assert key.deprecated is False
    assert len(str(key.key)) == 36
    assert APIkey.objects.all().count() == 1


def test_key_creation(db):
    """
    Factory should correctly create a new object without any errors.
    """
    key = APIkeyFactory()
    assert len(str(key.key)) == 36
    assert APIkey.objects.all().count()
