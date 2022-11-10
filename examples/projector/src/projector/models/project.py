from django.db import models


class Project(models.Model):
    class Meta:
        db_table = "project"

    name = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return "Project"
