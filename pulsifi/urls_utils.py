"""
    Utility functions provided for constructing URLs.
"""

from typing import Collection

from django.http import QueryDict
from django.urls import reverse
from django.utils.functional import lazy


def reverse_with_get_params(*args, **kwargs) -> str:
    """
        Returns a URL from the given view name, with the given get_params
        appended to the end.
    """

    get_params: dict[str, ...] = kwargs.pop("get_params", {})
    url: str = reverse(*args, **kwargs)
    if not get_params:
        return url

    qdict = QueryDict("", mutable=True)
    for key, val in get_params.items():
        if isinstance(val, Collection) and not isinstance(val, str):
            qdict.setlist(key, list(val))
        else:
            qdict[key] = val

    return url + "?" + qdict.urlencode()


reverse_with_get_params_lazy = lazy(reverse_with_get_params, str)
"""
    A lazily evaluated version of the reverse_with_get_params function, that
    returns a URL from the given view name, with the given get_params appended
    to the end.
"""
