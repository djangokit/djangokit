from django.db import models


class Page(models.Model):
    class Meta:
        db_table = "page"

    def __str__(self):
        return "Page"
