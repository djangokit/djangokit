from django.db import models


class Page(models.Model):
    class Meta:
        db_table = "page"

    title = models.CharField(max_length=255)
    content = models.TextField()

    def __str__(self):
        return "Page"
