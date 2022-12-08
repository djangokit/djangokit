from datetime import datetime
from typing import Optional

from django.db import models

from . import schema


class BlogPostSchema(schema.BaseModel):
    title: str
    slug: str
    lead: Optional[schema.Markdown] = None
    content: schema.Markdown
    created: datetime
    updated: datetime
    published: Optional[datetime] = None


class BlogPost(models.Model):
    class Meta:
        db_table = "blog_post"

    serialize = lambda self: BlogPostSchema.from_orm(self).dict()

    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    lead = models.TextField(null=True, blank=True)
    content = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    published = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return "BlogPost"
