from typing import Union, List, Dict
from pydantic import BaseModel, model_validator


class Query(BaseModel):
    index: str
    from_: Union[int, None] = 0
    size: Union[int, None] = 10
    key_words: Dict[str, str]
    offset: Union[List[str], None] = None

    @model_validator(mode='before')
    def check_from_offset(cls, values):
        offset = values.get("offset")
        from_ = values.get("from_")
        if offset is not None and (from_ is not None and from_ != 0):
            raise ValueError("When offset is provided, from_ must be 0 or None.")
        return values