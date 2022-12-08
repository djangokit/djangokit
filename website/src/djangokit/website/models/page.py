from datetime import datetime
from typing import Optional

from django.db import models

from . import schema


class PageSchema(schema.BaseModel):
    title: str
    slug: str
    lead: Optional[schema.Markdown] = None
    content: schema.Markdown
    created: datetime
    updated: datetime
    published: bool
    order: int


class Page(models.Model):
    class Meta:
        db_table = "page"
        ordering = ["order", "title"]

    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    lead = models.TextField(null=True, blank=True)
    content = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    published = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0, null=False)

    serialize = lambda self: PageSchema.from_orm(self).dict()

    @property
    def is_doc(self):
        return self.slug.startswith("doc-")

    def __str__(self):
        prefix = "[DOC] " if self.is_doc else ""
        return (
            f"{prefix}Page: {self.title} "
            f"(slug={self.slug}, published={self.published}, order={self.order})"
        )
