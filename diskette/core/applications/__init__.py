from django.utils.functional import lazy

from .definitions import ApplicationConfig, DrainApplicationConfig
from .resolver import AppModelResolverAbstract
from .store import DjangoAppLookupStore


def _get_appstore():
    return DjangoAppLookupStore()


# TODO: Not sure about lazy this since priority is to be memoized, then possibly lazy
get_appstore = lazy(_get_appstore, DjangoAppLookupStore)


__all__ = [
    "ApplicationConfig",
    "AppModelResolverAbstract",
    "DjangoAppLookupStore",
    "DrainApplicationConfig",
    "get_appstore",
]
