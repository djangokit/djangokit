from django.db import models
from marshmallow import Schema, fields

from . import schema


class PageSchema(Schema):
    id = fields.Integer(required=True)
    title = fields.String(required=True)
    slug = fields.String(required=True)
    lead = schema.MarkdownField()
    content = schema.MarkdownField(required=True)
    created = fields.DateTime(required=True)
    updated = fields.DateTime(required=True)
    published = fields.Boolean(required=True)


class Page(models.Model):
    class Meta:
        db_table = "page"

    serializer_factory = PageSchema

    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    lead = models.TextField(null=True, blank=True)
    content = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    published = models.BooleanField(default=False)

    def __str__(self):
        return f"Page: {self.title} ({self.slug})"
