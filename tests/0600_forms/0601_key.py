from diskette.factories import APIkeyFactory
from diskette.models import APIkey
from diskette.forms import APIkeyAdminForm
from diskette.utils.tests import compact_form_errors, build_post_data_from_object


def test_key_form_creation(db):
    """
    Key creation from admin form should just work without error and creating a new
    key will run the deprecation routine so there is always only one deprecated key.
    """
    # Build initial POST data
    data = build_post_data_from_object(
        APIkey,
        APIkeyFactory.build(),
        ignore=["id", "key"]
    )

    f = APIkeyAdminForm(data)
    assert f.is_valid() is True
    assert compact_form_errors(f) == {}

    created = f.save()
    assert APIkey.objects.all().count() == 1
    assert len(str(created.key)) == 36

    # Directly create a new non deprecated through factory/model so there is no
    # auto deprecation routine
    APIkeyFactory(deprecated=False)

    assert APIkey.objects.all().count() == 2
    assert APIkey.objects.filter(deprecated=False).count() == 2

    # Create a new key from form so the deprecation routine will be runned
    data = build_post_data_from_object(
        APIkey,
        APIkeyFactory.build(),
        ignore=["id", "key"]
    )
    f = APIkeyAdminForm(data)
    assert f.is_valid() is True
    created = f.save()

    # Deprecation routine has deprecated previous keys
    assert APIkey.objects.all().count() == 3
    assert APIkey.objects.filter(deprecated=False).count() == 1


def test_key_form_create_deprecated(db):
    """
    Form should never create an already deprecated key.
    """
    built = APIkeyFactory.build(deprecated=True)

    # Build initial POST data
    data = build_post_data_from_object(APIkey, built, ignore=["id", "key"])

    f = APIkeyAdminForm(data)
    # NOTE: Validation error is not raised with deprecated set to true from factory
    # since the creation form disable this field and so it is ignored when submitted.
    assert f.is_valid() is True
    assert compact_form_errors(f) == {}

    created = f.save()
    assert APIkey.objects.all().count() == 1
    assert created.deprecated is False


def test_key_form_change_deprecated(db):
    """
    Change form should only allow to deprecate an available key.
    """
    created = APIkeyFactory(deprecated=False)

    # Available key can be deprecated
    data = build_post_data_from_object(APIkey, created, ignore=["id", "key"])
    data["deprecated"] = True
    f = APIkeyAdminForm(data, instance=created)
    assert f.is_valid() is True
    modified = f.save()
    assert modified.deprecated is True

    # Deprecated key can not be made available anymore
    data = build_post_data_from_object(APIkey, created, ignore=["id", "key"])
    data["deprecated"] = False
    f = APIkeyAdminForm(data, instance=created)
    # NOTE: Validation error is not raised with 'deprecated' set to true from factory
    # since the creation form disable this field and so it is ignored when submitted.
    assert f.is_valid() is True
    modified = f.save()
    # Value is still true since field is disabled, it can not be changed
    assert modified.deprecated is True
