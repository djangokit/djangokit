from markdown import markdown
from marshmallow import fields


class MarkdownField(fields.String):
    """Field that converts Markdown value to HTML on serialization."""

    def __init__(self, dump_only=True, **kwargs):
        super().__init__(dump_only=dump_only, **kwargs)

    def _serialize(self, value, *args, **kwargs):
        if value is None:
            return None
        return markdown(value)
