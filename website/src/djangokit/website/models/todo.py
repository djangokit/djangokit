from django.db import models
from django.utils.text import Truncator
from markdown import markdown


class TodoItem(models.Model):
    class Meta:
        db_table = "todo_item"

    content = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    completed = models.DateTimeField(null=True, blank=True)

    def as_dict(self):
        return {
            "id": self.id,
            "rawContent": self.content,
            "content": markdown(self.content),
            "created": self.created,
            "updated": self.updated,
            "completed": self.completed,
        }

    def __str__(self):
        truncator = Truncator(self.content)
        return f"TODO: {truncator.chars(50)}"
