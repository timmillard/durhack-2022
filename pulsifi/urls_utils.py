from django.http import QueryDict
from django.urls import reverse
from django.utils.functional import lazy


def reverse_with_get_params(*args, **kwargs) -> str:
    get_params = kwargs.pop("get_params", {})
    url = reverse(*args, **kwargs)
    if not get_params:
        return url

    qdict = QueryDict("", mutable=True)
    for key, val in get_params.items():
        if type(val) is list:
            qdict.setlist(key, val)
        else:
            qdict[key] = val

    return url + '?' + qdict.urlencode()


reverse_lazy_with_get_params = lazy(reverse_with_get_params, str)
