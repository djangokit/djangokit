from datetime import datetime
from typing import Optional

from django.db import models
from django.utils.text import Truncator
from pydantic import BaseModel, Field

from . import schema


class TodoItemSchema(BaseModel):
    class Config:
        orm_mode = True

    id: int
    rawContent: str = Field(..., alias="content")
    content: schema.Markdown
    created: datetime
    updated: datetime
    completed: Optional[datetime] = None


class TodoItem(models.Model):
    class Meta:
        db_table = "todo_item"

    serialize = lambda self: TodoItemSchema.from_orm(self).dict()

    content = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    completed = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        truncator = Truncator(self.content)
        return f"TODO: {truncator.chars(50)}"
