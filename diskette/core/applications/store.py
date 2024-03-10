from functools import cache

from django.utils.functional import lazy

from .lookupstore import DjangoAppLookupStore


@cache
def _get_appstore():
    """
    Cached function to initialize the application store.
    """
    return DjangoAppLookupStore()


get_appstore = lazy(_get_appstore, DjangoAppLookupStore)
