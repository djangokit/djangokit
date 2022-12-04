from functools import lru_cache

from markdown import Markdown


@lru_cache(maxsize=None)
def get_instance() -> Markdown:
    """Create and cache a configured Markdown converter.

    This centralizes the Markdown config and avoids the overhead of
    creating a new instance for every request.

    """
    return Markdown(
        extensions=[
            "admonition",  # !!! note
            "attr_list",  # {: .add-this-class }
            "fenced_code",  # ```...```
            "codehilite",  # Highlight code blocks with Pygments
            "nl2br",  # Render newlines as hard breaks
            "toc",  # [TOC]
        ]
    )


def markdown(text: str) -> str:
    """Convert Markdown text to HTML.

    This uses our configured singleton `Markdown` instance and should
    be used instead of :func:`markdown.markdown`.

    """
    return get_instance().convert(text)
