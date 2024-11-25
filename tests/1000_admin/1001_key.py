from diskette.factories import APIkeyFactory
from diskette.models import APIkey
from diskette.utils.tests import (
    get_admin_add_url, get_admin_change_url, get_admin_list_url,
)


def test_key_admin_ping_add(db, admin_client):
    """
    APIkey model admin add form view should not raise error on GET request.
    """
    url = get_admin_add_url(APIkey)
    response = admin_client.get(url)

    assert response.status_code == 200


def test_key_admin_ping_list(db, admin_client):
    """
    APIkey model admin list view should not raise error on GET request.
    """
    url = get_admin_list_url(APIkey)
    response = admin_client.get(url)

    assert response.status_code == 200


def test_key_admin_ping_detail(db, admin_client):
    """
    APIkey model admin detail view should not raise error on GET request.
    """
    obj = APIkeyFactory()

    url = get_admin_change_url(obj)
    response = admin_client.get(url)

    assert response.status_code == 200
