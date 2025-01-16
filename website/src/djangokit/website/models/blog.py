from datetime import datetime
from typing import Optional

from django.conf import settings
from django.db import models
from django.utils.text import Truncator

from ..markdown import markdown
from . import schema


class AuthorSchema(schema.BaseModel):
    first_name: str
    last_name: str
    email: str
    username: str


class BlogPostSchema(schema.BaseModel):
    title: str
    slug: str
    author: AuthorSchema
    lead: Optional[schema.Markdown] = None
    content: schema.Markdown
    blurb: str
    created: datetime
    updated: datetime
    published: Optional[datetime] = None


class BlogPost(models.Model):
    class Meta:
        db_table = "blog_post"

    serialize = lambda self: BlogPostSchema.model_validate(self).model_dump()

    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, models.PROTECT)
    lead = models.TextField(null=True, blank=True)
    content = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    published = models.DateTimeField(null=True, blank=True)

    @property
    def blurb(self) -> str:
        """Get HTML preview blurb."""
        html_content = markdown(self.content)
        truncator = Truncator(html_content)
        return truncator.chars(100, html=True)

    def __str__(self):
        return f"Blog Post: {self.title} @ {self.slug}"


class BlogComment(models.Model):
    class Meta:
        db_table = "blog_comment"

    email = models.EmailField()
    name = models.CharField(max_length=255)
    content = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    post = models.ForeignKey(BlogPost, models.DO_NOTHING, related_name="comments")

    def __str__(self):
        return f"Blog Comment by {self.email}"
