from functools import reduce


def merge_dicts(*dicts) -> dict:
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
