from functools import cache

from django.utils.functional import lazy

from .lookupstore import DjangoAppLookupStore


@cache
def _get_appstore():
    return DjangoAppLookupStore()


get_appstore = lazy(_get_appstore, DjangoAppLookupStore)
