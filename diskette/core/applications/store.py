from django.utils.functional import lazy

from .lookupstore import DjangoAppLookupStore


def _get_appstore():
    return DjangoAppLookupStore()


# TODO: Not sure about lazy this since priority is to be memoized, then possibly lazy
get_appstore = lazy(_get_appstore, DjangoAppLookupStore)
