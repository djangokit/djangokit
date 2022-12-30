from functools import lru_cache, reduce
from hashlib import sha1
from typing import Any

from django.middleware import csrf


def get_unmasked_csrf_token(request):
    """Get unmasked CSRF token for `request`."""
    masked_csrf_token = csrf.get_token(request)
    return csrf._unmask_cipher_token(masked_csrf_token)


@lru_cache()
def make_cache_key(*parts: Any) -> str:
    """Make a cache key from the given parts.

    The parts will be stringified and joined with a colon. That string
    will then be hashed and the hex digest will be returned as the cache
    key.

    """
    key = ":".join((str(p) for p in parts))
    return sha1(key.encode("utf-8")).hexdigest()


def merge_dicts(*dicts: dict) -> dict:
    """Merge dictionaries recursively."""
    return reduce(_merge_dicts, dicts, {})


def _merge_dicts(a: dict, b: dict) -> dict:
    a = a.copy()
    if not (isinstance(a, dict) and isinstance(b, dict)):
        raise TypeError(f"Expected two dicts; got {a.__class__} and {b.__class__}")
    for k, v in b.items():
        if k in a and isinstance(a[k], dict):
            v = merge_dicts(a[k], v)
        a[k] = v
    return a
