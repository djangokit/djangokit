from ..markdown import markdown


class Markdown(str):
    """Field that converts Markdown value to HTML on serialization."""

    @classmethod
    def __get_validators__(cls):
        yield lambda v: markdown(v)
