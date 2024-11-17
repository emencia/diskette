import factory

from ..models import APIkey


class APIkeyFactory(factory.django.DjangoModelFactory):
    """
    Factory to create instance of a APIkey.
    """
    deprecated = False

    class Meta:
        model = APIkey
        skip_postgeneration_save = True
