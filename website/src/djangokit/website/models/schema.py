from typing import Annotated

import pydantic
from pydantic import AfterValidator, PlainSerializer, WithJsonSchema

from ..markdown import markdown


class BaseModel(pydantic.BaseModel):
    model_config = {
        "from_attributes": True,
    }

    id: int


"""Field type that converts Markdown value to HTML on serialization."""

Markdown = Annotated[
    str,
    AfterValidator(lambda v: markdown(v)),
    PlainSerializer(lambda v: markdown(v), return_type=str),
    WithJsonSchema({"type": "string"}, mode="serialization"),
]
