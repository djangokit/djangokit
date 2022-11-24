from django.db import models


class Page(models.Model):
    class Meta:
        db_table = "page"

    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    lead = models.TextField(null=True, blank=True)
    content = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    published = models.BooleanField(default=False)

    def __str__(self):
        return f"Page: {self.title}"
