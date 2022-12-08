import pydantic

from ..markdown import markdown


class BaseModel(pydantic.BaseModel):
    class Config:
        orm_mode = True

    id: int


class Markdown(str):
    """Field that converts Markdown value to HTML on serialization."""

    @classmethod
    def __get_validators__(cls):
        yield lambda v: markdown(v)
