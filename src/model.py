from typing import Any, Union, List
from pydantic import BaseModel


class Query(BaseModel):
    index: str
    from_: Union[int, None] = 0
    size: Union[int, None] = 2
    key_words: dict
    offset: Union[List[Any], None] = None
