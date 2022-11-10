from functools import lru_cache
from urllib.parse import urlparse


@lru_cache(maxsize=None)
def is_site_path(url: str) -> bool:
    """Is the URL a site path?

    Determines whether the URL is a path like "/" or "/docs". This can
    be used, for example, in a login view to ensure the redirect
    location provided in the `next` query parameter is valid.

    """
    result = urlparse(url)
    return not result.netloc
